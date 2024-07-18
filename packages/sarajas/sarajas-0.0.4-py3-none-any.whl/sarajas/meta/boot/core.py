# class Datum():
#     def __init__(self, datum):
#         self._type = datum[0]
#         self.value = datum[1]
#     def __str__(self):
#         return str(self.value)
# class Item():
#     def __init__(self, ID='0', item_dict=None):
#         if item_dict:
#             self._unpack(item_dict)
#         else:
#             self._unpack(_load_by_name(ID=str(ID)))
#         if '_init_executable' in self.__dict__:
#             exec(self._init_executable[1])
#     def _unpack(self, item_dict):
#         self.__dict__ = {key: Datum(datum_tuple) for key, datum_tuple in item_dict.items()}
#     def add_key(self,key='test', dtype='_python_str', value='value'):
#         self.__dict__.update({key: Datum((dtype, value))})
#     def write(self):
#         """Packs and writes the item back."""
#         packed_dict = {key: (d._type, d.value) for key, d in self.__dict__.items()}
#         path = path_data/(str(self.__ID__) + '.' + file_extension)
#         with open(path, 'w+') as file:
#             yaml.dump(packed_dict, file, default_flow_style=False)
#     def execute(self,**kwargs):
#         exec(self.executable[1])
#     def __str__(self):
#         string  = ''
#         for key, datum in self.__dict__.items():
#             string += '\nKey: %s:' % (key)
#             string += '\tType: %s' % (datum._type)
#             string += '\tValue: \n%s' % (str(datum))
#         return string
# def _regenerate_boot(path = path_data / '0.aedb'):
#     meta.constructor.generate_boot(path)
# def _regenerate_config(path = path_data / '1.aedb'):
#     meta.constructor.generate_config(path)
# _boot = Item(ID='0')
# _config = Item(ID='1')
# _types = Item(ID=_config._types.value)
# _metaindex = Item(ID=_config._metaindex.value)
# print(_config.logo)
# print(_config.intro)
# try:
#     prompt = ash + ': ' # Stupid hack to get the symbol
#     while True:
#         print(prompt, end='')
#         exec('\n'.join(iter(input, '')))
# except KeyboardInterrupt:
#     pass
