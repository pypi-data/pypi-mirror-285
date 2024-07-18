#  Copyright: Contributors to the sts project
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import testinfra.host
from testinfra.host import Host


def host_init() -> testinfra.host.Host:
    """Get testinfra host with local backend."""
    return Host.get_host('local://')


host = host_init()
if not host.exists('ip'):
    host.run('dnf install -y iproute')
