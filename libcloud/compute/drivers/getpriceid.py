from libcloud.common.softlayer import SoftLayerConnection
from libcloud.compute.base import NodeDriver
from libcloud.compute.types import Provider
import xlsxwriter
priceids = xlsxwriter.Workbook('price_ids.xlsx')
sheet = priceids.add_worksheet()

class SoftLayerNodeDriver(NodeDriver):

    connectionCls = SoftLayerConnection
    name = 'SoftLayer'
    website = 'http://www.softlayer.com/'
    type = Provider.SOFTLAYER
    api_name = 'softlayer'

    row = 0
    col = 0

    # Get package id
    def _get_package_id(self, package_type):
        package_id_info = {package['name']: package['id'] for
                           package in self.connection.request('SoftLayer_Product_Package', 'getAllObjects').object
                           if package['name'] == package_type.title()}
        return package_id_info  # returns a dictionary {'Endurance' : 240}

    def _get_os_type(self, os):
        return [{'id': os_type['id'], 'keyName': os_type['keyName']}
                for os_type in
                self.connection.request('SoftLayer_Network_Storage_Iscsi_OS_Type', 'getAllObjects').object
                if os_type['name'] == os.title()]

    def _get_datacenter(self, location):
        return [datacenter['id']
                for datacenter in self.connection.request('SoftLayer_Location', 'getDatacenters').object
                if datacenter['longName'] == location.title()]

    def create_volume(self, **kwargs):
        storage_type = kwargs['storage_type'].title() + ' Storage'  # Block storage
        package_info = self._get_package_id(kwargs['storage_package'])  # Getting package name and id {'Endurance': 240}
        package_id = package_info[kwargs['storage_package'].title()]  # package id  240
        storage_tier_level = kwargs['storage_tier'] + ' IOPS per GB'  # tier level value 0.25 IOPS per GB
        storage_space = kwargs['storage_size'] + ' GB Storage Space'  # storage space value 20 GB Storage Space
        snapshot_space_size = kwargs['snapshot_size']
        os_type = self._get_os_type(kwargs['os'])[0]  # {'keyName': 'LINUX', 'id': 12}
        datacenter_id = self._get_datacenter(kwargs['location'])[0]  # 3

        items = self.connection.request('SoftLayer_Product_Package', 'getItems', id=package_info.values()[0]).object
        for item in items:
            #print item
            #print package_info.values(), package_info.keys()
            if item['itemCategory']['name'] == package_info.keys()[0]:
                package_price_id = item['prices'][0]['id']
                #print package_price_id
            if item['description'] == storage_type:
                storage_type_price_id = item['prices'][0]['id']
                #print  storage_type_price_id
            if item['description'] == storage_tier_level:
                storage_tier_level_price_id = item['prices'][0]['id']
                #print storage_tier_level_price_id
            if item['description'] == storage_space:
                for each in item['prices']:
                    storage_space_price_id = each['id']

                    price_id = [{'id': 45098}, #package_price_id},
                                {'id': 45058}, # storage_type_price_id},
                                {'id': 45068}, #storage_tier_level_price_id},
                                {'id': storage_space_price_id}]
                                        #'id' : 45118}
                    #print price_id

                    newvolume = {
                        'complexType': "SoftLayer_Container_Product_Order_Network_Storage_Enterprise",
                        'packageId': package_id,
                        'location': datacenter_id,
                        "osFormatType": os_type,
                        'prices': price_id,
                        "quantity": kwargs['quantity']
                    }

                    try:
                        self.connection.request('SoftLayer_Product_Order', 'verifyOrder', newvolume).object
                        print storage_space, 45098, 45058, 45068, storage_space_price_id, 'success'
                        sheet.write(self.row, self.col, storage_space)
                        sheet.write(self.row, self.col+1, 45058) #package_price_id)
                        sheet.write(self.row, self.col+2, 45098) #storage_type_price_id)
                        sheet.write(self.row, self.col+3, 45068) #storage_tier_level_price_id)
                        sheet.write(self.row, self.col+4, storage_space_price_id)
                        sheet.write(self.row, self.col+5, 'success')
                        self.row += 1
                    except:
                        print storage_space, storage_space_price_id, 'fail'
                        sheet.write(self.row, self.col, storage_space)
                        sheet.write(self.row, self.col + 1, 45058)  # package_price_id)
                        sheet.write(self.row, self.col + 2, 45098)  # storage_type_price_id)
                        sheet.write(self.row, self.col + 3, 45068)  # storage_tier_level_price_id)
                        sheet.write(self.row, self.col + 4, storage_space_price_id)
                        sheet.write(self.row, self.col + 5, 'fail')
                        self.row += 1

# Calling the above functions
user_name = ''
api_key = ''

storage_space_options = ['20', '40', '80', '100', '250', '500', '1000', '2000', '4000', '8000', '12000']

ordering = SoftLayerNodeDriver(user_name, api_key)
for space in storage_space_options:
    ordering.create_volume(storage_type='block', storage_package='endurance',
                       storage_tier='0.25', storage_size=space, snapshot_size='5',
                       location='Dallas 1', os='linux', quantity='1')

priceids.close()
