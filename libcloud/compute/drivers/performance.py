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
        package_id_info = {package['name']: package['id'] for
                           package in self.connection.request('SoftLayer_Product_Package', 'getAllObjects').object
                           if package['name'] == package_type.title()}
        return package_id_info  # returns a dictionary {'Endurance' : 240}

    def _get_os_type(self, os):
        return [{'id': os_type['id'], 'keyName': os_type['keyName']}
                for os_type in self.connection.request('SoftLayer_Network_Storage_Iscsi_OS_Type', 'getAllObjects').object
                if os_type['name'] == os.title()]

    def _get_datacenter(self, location):
        return [datacenter['id']
                for datacenter in self.connection.request('SoftLayer_Location', 'getDatacenters').object
                if datacenter['longName'] == location.title()]

    def _get_price_ids(self, storage_type, package_info, storage_space):
        items = self.connection.request('SoftLayer_Product_Package', 'getItems', id=package_info.values()[0]).object
        prices = [  # package price id
            {'id': item['prices'][0]['id'] for item in items if item['itemCategory']['name'] == package_info.keys()[0]},
            # storage_type_price_id
            {'id': item['prices'][0]['id'] for item in items if item['description'] == storage_type},
            # storage_tier_level_price_id
            #{'id': item['prices'][0]['id'] for item in items if item['description'] == tier_level},
            # storage_space_price_id
            {'id' : item['prices'][0]['id'] for item in items if item['description'] == storage_space} # 46649 is the output
            #{'id': endurance_storage_space_price_id.get(storage_space)}
            ##TODO GET PRICE ID FOR SNAPSHOT

        ]
        return prices

    def create_volume(self, **kwargs):
        storage_type = kwargs['storage_type'].title() + ' Storage'  # Block storage
        package_info = self._get_package_id(kwargs['storage_package'])  # Getting package name and id {'Endurance': 240}
        package_id = package_info[kwargs['storage_package'].title()]  # package id  240
        #storage_tier_level = kwargs['storage_tier'] + ' IOPS per GB'  # tier level value 0.25 IOPS per GB
        storage_space = kwargs['storage_size']  # + ' GB Storage Space'   # storage space value 20 GB Storage Space
        iops = kwargs['iops']
        #snapshot_space_size = kwargs['snapshot_size']
        os_type = self._get_os_type(kwargs['os'])[0]  # {'keyName': 'LINUX', 'id': 12}
        datacenter_id = self._get_datacenter(kwargs['location'])[0]  # 3

        # Getting the prices
        package_price_id = self._get_price_ids(storage_type, package_info, storage_space)
        # [{'id': 45058}, {'id': 45098}, {'id': 45068}, {'id': 45118}]
        print storage_type, package_info, package_id, storage_space, os_type, datacenter_id, package_price_id

        '''newvolume = {
            'complexType': "SoftLayer_Container_Product_Order_Network_Storage_Enterprise",
            'packageId': package_id,
            'location': datacenter_id,
            'storage_package': storage_package,
            'storage_size': storage_size,
            'snapshot_space_size': snapshot_space_size,
            'os': 12,
            'iops': iops,
            'prices': [{'id': 40762},  # storage_type_price_id},
                       {'id': 40682},  # storage_space_price_id},
                       {'id': 40792}  # iops_price_id}
                       ],
            "quantity": 1
        }

        self.connection.request('SoftLayer_Product_Order', 'verifyOrder', newvolume).object'''


# Calling the above functions
user_name = ''
api_key = ''

ordering = SoftLayerNodeDriver(user_name, api_key)

ordering.create_volume(storage_type='block',
                             storage_package='performance',
                             #storage_tier='0.25',
                             storage_size='20',
                             iops = '100',
                             #snapshot_size='5',
                             location='Dallas 1',
                             os='linux',
                             quantity='1')
