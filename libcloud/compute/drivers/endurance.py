from libcloud.common.softlayer import SoftLayerConnection
from libcloud.compute.base import NodeDriver
from libcloud.compute.types import Provider

class SoftLayerNodeDriver(NodeDriver):

    connectionCls = SoftLayerConnection
    name = 'SoftLayer'
    website = 'http://www.softlayer.com/'
    type = Provider.SOFTLAYER
    api_name = 'softlayer'

    # Get package id
    def _get_package_id(self, package_type):
        package_id_info = {package['name'] : package['id'] for
                package in self.connection.request('SoftLayer_Product_Package', 'getAllObjects').object
                       if package['name'] == package_type.title()}
        return package_id_info    # returns a dictionary {'Endurance' : 240}

    def _get_price_ids(self, storage_type, package_info, tier_level, storage_space):
        endurance_storage_space_price_id = {'20':45118, '40':45148, '80':45178, '100':45208, '250':45238, '500':45268,
                                  '1000':45298, '2000':45328, '4000':45358, '8000':45388, '12000':45418}
        items = self.connection.request('SoftLayer_Product_Package','getItems', id=package_info.values()[0]).object
        prices = [ # package price id
                   {'id' : item['prices'][0]['id'] for item in items if item['itemCategory']['name'] == package_info.keys()[0]},
                   # storage_type_price_id
                   {'id' : item['prices'][0]['id'] for item in items if item['description'] == storage_type},
                   # storage_tier_level_price_id
                   {'id': item['prices'][0]['id'] for item in items if item['description'] == tier_level},
                   # storage_space_price_id
                   #{'id' : item['prices'][0]['id'] for item in items if item['description'] == storage_space} # 46649 is the output
                   {'id' : endurance_storage_space_price_id.get(storage_space)}
            ##TODO GET PRICE ID FOR SNAPSHOT

        ]
        return prices

    def _get_os_type(self, os):
        return [{'id': os_type['id'], 'keyName': os_type['keyName']}
                for os_type in self.connection.request('SoftLayer_Network_Storage_Iscsi_OS_Type', 'getAllObjects').object
                if os_type['name'] == os.title()]

    def _get_datacenter(self, location):
        return [datacenter['id']
                for datacenter in self.connection.request('SoftLayer_Location','getDatacenters').object
                if datacenter['longName'] == location.title()]

    def create_volume(self, **kwargs):
        storage_type = kwargs['storage_type'].title() + ' Storage'       # Block storage
        package_info = self._get_package_id(kwargs['storage_package'])    # Getting package name and id {'Endurance': 240}
        package_id = package_info[kwargs['storage_package'].title()]     # package id  240
        storage_tier_level = kwargs['storage_tier'] + ' IOPS per GB'    # tier level value 0.25 IOPS per GB
        storage_space = kwargs['storage_size'] # + ' GB Storage Space'   # storage space value 20 GB Storage Space
        snapshot_space_size = kwargs['snapshot_size']
        os_type = self._get_os_type(kwargs['os'])[0]                    #  {'keyName': 'LINUX', 'id': 12}
        datacenter_id = self._get_datacenter(kwargs['location'])[0]       # 3

        # Getting the prices
        package_price_id = self._get_price_ids(storage_type, package_info, storage_tier_level, storage_space)
                               #[{'id': 45058}, {'id': 45098}, {'id': 45068}, {'id': 45118}]
        print storage_type, package_info, package_id, storage_tier_level, storage_space, os_type, datacenter_id, package_price_id

        newvolume = {
            'complexType': "SoftLayer_Container_Product_Order_Network_Storage_Enterprise",
            'packageId': package_id ,
            'location': datacenter_id,
            "osFormatType": os_type,
            'prices': package_price_id,
            "quantity": kwargs['quantity']
        }

        self.connection.request('SoftLayer_Product_Order', 'verifyOrder', newvolume).object


# Calling the above functions
user_name = 'ranganath_achari'
api_key = '6869a91aa3eef9b67b0442a03e94e1a5d32569b7991dd20e061a1f42e1b5298d'

ordering = SoftLayerNodeDriver(user_name, api_key)
storage_space_options = ['20', '40', '80', '100', '250', '500', '1000', '2000', '4000', '8000', '12000']
for space in storage_space_options:
    ordering.create_volume(storage_type='block', storage_package='endurance',
                       storage_tier='0.25', storage_size=space, snapshot_size='5',
                       location='Dallas 1', os='linux', quantity='1')