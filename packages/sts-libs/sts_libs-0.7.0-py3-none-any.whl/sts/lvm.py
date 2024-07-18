"""lvm.py: Module with test specific method for LVM."""

#  Copyright: Contributors to the sts project
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import annotations

import fileinput
import logging
import re
from abc import ABC, ABCMeta
from functools import partialmethod, wraps
from typing import TYPE_CHECKING, Any, ClassVar, TypeVar

from sts.utils.cmdline import run, run_ret_out

if TYPE_CHECKING:
    from testinfra.backend.base import CommandResult


###########################################
# PV section
###########################################
def pv_query():  # noqa: ANN201
    """Query Physical Volumes and return a dictionary with PV information for each PV.
    The arguments are:
    None
    Returns:
    dict: Return a dictionary with PV info for each PV.
    """
    cmd = 'pvs --noheadings --separator ","'
    retcode, output = run_ret_out(cmd, return_output=True)
    if retcode != 0:
        logging.debug('there are no VGs')
        return None
    pvs = output.split('\n')

    # format of PV info: PV,VG,Fmt,Attr,PSize,PFree
    pv_info_regex = r'\s+(\S+),(\S+)?,(\S+),(.*),(.*),(.*)$'

    pv_dict = {}
    for pv in pvs:
        m = re.match(pv_info_regex, pv)
        if not m:
            # logging.warning("(%s) does not match vgdisplay output format" % vg)
            continue
        pv_info_dict = {
            'vg': m.group(2),
            'fmt': m.group(3),  # not sure what it is
            'attr': m.group(4),
            'psize': m.group(5),
            'pfree': m.group(6),
        }
        pv_dict[m.group(1)] = pv_info_dict

    return pv_dict


###########################################
# Config file
###########################################


def get_config_file_path():  # noqa: ANN201
    return '/etc/lvm/lvm.conf'


def update_config(key: str, value: str):  # noqa: ANN201
    config_file = get_config_file_path()
    search_regex = re.compile(r'(\s*)%s(\s*)=(\s*)\S*' % key)  # noqa: UP031
    search_regex_with_comment = re.compile(r'(\s*#\s*)%s(\s*)=(\s*)\S*' % key)  # noqa: UP031
    for line in fileinput.input(config_file, inplace=True):
        m = search_regex.match(line)
        m_with_comment = search_regex_with_comment.match(line)
        if m:
            line = f'{m.group(1)}{key} = {value}'  # noqa: PLW2901
        if m_with_comment:
            line = f"{m_with_comment.group(1).replace('#', '')}{key} = {value}"  # noqa: PLW2901
        # print saves the line to the file
        # need to remove new line character as print will add it
        line = line.rstrip('\n')  # noqa: PLW2901
        print(line)


def get_lvm_config_options(all_params=False):  # noqa: ANN001, ANN201
    """Get all the configuration types from lvm.conf file."""
    out = run('lvmconfig --type full').stdout.rstrip()

    options = {}
    category = ''
    for line in out.split('\n'):
        line = line.strip()  # noqa: PLW2901
        if not line or '}' in line:
            # skip empty or end of list line
            continue
        if '{' in line:
            # category part
            category = line[:-2]  # removing "allocation {"[:-2] == "allocation"
            options[category] = []
        elif '=' in line:
            # content of a category
            options[category].append(line.split('=')[0])

    if not all_params:
        return options

    options_all = []
    for value in options.values():
        options_all.extend(value)
    return options_all


def check_lvm_config(option):  # noqa: ANN001, ANN201
    return run(f'lvs -o {option}').stdout.rstrip()


def get_all_lvm_config_options():  # noqa: ANN201
    all_opts = check_lvm_config('asdf')  # needs just something that it doesn't know
    # we need to test_filter on lines that look like this
    # lvm_blahblah - explanation
    # and remove separators

    # at the end is '?' which should not be there therefore [:-1]
    return [i.split()[0] for i in all_opts if re.match(r'.+-.+', i) and '--' not in i][:-1]


def run_cmd(func):  # noqa: ANN001, ANN201
    # TODO: Duplicate of run_command
    """Decorator for running commands
    kwargs need to be edited every time, so decorator is probably the best solution.
    """

    @wraps(func)
    def wrapped(*args, **kwargs):  # noqa: ANN002, ANN003, ANN202
        return run_ret_out(func(), *args, **kwargs, return_output=True)  # cmd == func()

    return wrapped


@run_cmd
def get_all_lvmvdoconfig_options():  # noqa: ANN201
    return 'lvmconfig --type list'


@run_cmd
def lvdisplay():  # noqa: ANN201
    return 'lvdisplay'


def print_profile_file(profile_name, path=None):  # noqa: ANN001, ANN201
    if not path:
        path = '/etc/lvm/profile'  # default profile location
    run(f'cat {path}/{profile_name}.profile')


def get_lvdisplay_data():  # noqa: ANN201
    _, out = lvdisplay()
    lines = next(line for line in out if 'LV Name' in line and 'pool' not in line).split()
    print(lines)
    return lines[-1]


def run_command(func):  # noqa: ANN001, ANN201
    """Decorator for running commands
    kwargs need to be edited every time, so decorator is probably the best solution.
    """

    @wraps(func)
    def wrapped(inst, **kwargs):  # noqa: ANN001, ANN003, ANN202
        inst.tmp_kwargs = kwargs
        # The first thing is to replace values that are
        # conf=fmf_conf_value -> conf=conf_value
        kwargs = inst.replace_multiple_option_values(**kwargs)
        # check configuration arguments from old conf to new
        # slab_size=minimum -> slab_size=compute(value)
        kwargs = inst.check_config_arguments(**kwargs)

        # create command
        cmd, kwargs = func(inst, **kwargs)

        # remove everything not necessary
        kwargs = inst.remove_nones(inst.remove_vdo_arguments(**kwargs))

        # Check
        if inst.check(**kwargs) is not True:  # check() with "the manual"
            print('Check failed.')
            return False

        # Run
        return inst.run(cmd, **kwargs)

    return wrapped


# ^^^ legacy
# ====================================================================
# sts code below


T = TypeVar('T', bound='LVM')


class LVMMeta(ABCMeta):
    def __new__(  # type: ignore[misc]
        cls: type[T], name: str, bases: tuple, namespace: dict[str, Any], **kwargs: dict[str, Any] | None
    ) -> T:
        new_cls = super().__new__(cls, name, bases, namespace, **kwargs)  # type: ignore[misc]
        if 'commands' in namespace:
            for command in namespace['commands']:
                setattr(new_cls, command, partialmethod(new_cls.lvm_run, command))
        return new_cls


class LVM(ABC, metaclass=LVMMeta):
    def __init__(self, yes: bool = True, force: bool = False) -> None:
        self.yes = yes
        self.force = force

    def lvm_run(
        self,
        cli_name: str,
        options: list[str] | None = None,
    ) -> CommandResult:
        command_list: list[str] = [cli_name]
        if self.yes:
            command_list.append('--yes')
        if self.force:
            command_list.append('--force')
        if options:
            command_list.extend(options)
        command: str = ' '.join(command_list)
        return run(command)


class PV(LVM):
    commands: ClassVar = [
        'pvchange',
        'pvck',
        'pvcreate',
        'pvdisplay',
        'pvmove',
        'pvremove',
        'pvresize',
        'pvs',
        'pvscan',
    ]

    # This is where any future pv-related functions would go


class VG(LVM):
    commands: ClassVar = [
        'vgcfgbackup',
        'vgcfgrestore',
        'vgchange',
        'vgck',
        'vgconvert',
        'vgcreate',
        'vgdisplay',
        'vgexport',
        'vgextend',
        'vgimport',
        'vgimportclone',
        'vgimportdevices',
        'vgmerge',
        'vgmknodes',
        'vgreduce',
        'vgremove',
        'vgrename',
        'vgs',
        'vgscan',
        'vgsplit',
    ]


class LV(LVM):
    commands: ClassVar = [
        'lvchange',
        'lvm',
        'lvm_import_vdo',
        'lvremove',
        'lvconvert',
        'lvmconfig',
        'lvmpolld',
        'lvrename',
        'lvcreate',
        'lvmdevices',
        'lvmsadc',
        'lvresize',
        'lvdisplay',
        'lvmdiskscan',
        'lvmsar',
        'lvs',
        'lvextend',
        'lvmdump',
        'lvreduce',
        'lvscan',
    ]

    def vdocreate(self, options: list[str] | None) -> CommandResult:
        opts = ['--type', 'vdo']
        if options:
            opts += options
        return self.lvcreate(opts)  # type: ignore[attr-defined]
