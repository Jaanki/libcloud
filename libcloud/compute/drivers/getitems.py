from libcloud.common.softlayer import SoftLayerConnection
from libcloud.compute.base import NodeDriver
from libcloud.compute.types import Provider

class SoftLayerNodeDriver(NodeDriver):

    connectionCls = SoftLayerConnection
    name = 'SoftLayer'
    website = 'http://www.softlayer.com/'
    type = Provider.SOFTLAYER
    api_name = 'softlayer'


    def get_storage_type_price_id(self, package_id):
        # Getting the storage NFS price id.
        items = self.connection.request('SoftLayer_Product_Package', 'getItems', id=package_id).object
        for item in items:
            print item


# Calling the above functions
user_name = ''
api_key = ''

ordering = SoftLayerNodeDriver(user_name, api_key)
ordering.get_storage_type_price_id(222)


storage_space_options = ['20', '40', '80', '100', '250', '500', '1000', '2000', '4000', '8000', '12000']
#for space in storage_space_options:
#    ordering.create_volume(storage_type='block', storage_package='endurance',
#                       storage_tier='0.25', storage_size=space, snapshot_size='5',
#                       location='Dallas 1', os='linux', quantity='1')

#ordering.create_volume(storage_type='block', storage_package='endurance',
                     #  storage_tier='0.25',storage_size='20',snapshot_size='5',
                     #  location='Dallas 1',os='linux',quantity='3')
