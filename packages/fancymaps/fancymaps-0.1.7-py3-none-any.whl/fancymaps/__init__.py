#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.colors as mpl_c

vabcb_list = ['#fb8d62', '#f7875e', '#f2815a', '#ee7b57', '#e97553', '#e56f4f',
              '#e0694b', '#dc6248', '#d75c44', '#d35640', '#ce503c', '#ca4a39',
              '#c54435', '#c13e31', '#bc382d', '#b8322a', '#b32c26', '#b22b24',
              '#b63627', '#bb412a', '#bf4b2d', '#c45630', '#c96133', '#cd6b36',
              '#d27639', '#d6803b', '#db8b3e', '#df9641', '#e4a044', '#e9ab47',
              '#edb64a', '#f2c04d', '#f6cb50', '#fbd653', '#fcdb5a', '#fddd65',
              '#fddf6f', '#fde179', '#fde484', '#fde68e', '#fde898', '#feeba2',
              '#feedad', '#feefb7', '#fef1c1', '#fef4cc', '#fef6d6', '#fff8e0',
              '#fffaea', '#fffdf5', '#ffffff', '#f5fefb', '#ecfdf8', '#e2fbf4',
              '#d9faf0', '#cff9ed', '#c6f8e9', '#bcf6e6', '#b3f5e2', '#a9f4de',
              '#a0f3db', '#96f2d7', '#8df0d3', '#83efd0', '#7aeecc', '#70edc8',
              '#67ebc5', '#61e7c1', '#61ddbf', '#62d4bc', '#63cab9', '#64c0b6',
              '#65b6b3', '#66acb1', '#66a2ae', '#6798ab', '#688ea8', '#6984a5',
              '#6a7aa3', '#6b71a0', '#6b679d', '#6c5d9a', '#6d5397', '#6e4995',
              '#6f4a98', '#70509d', '#7156a3', '#715ca9', '#7262ae', '#7368b4',
              '#746fba', '#7575bf', '#767bc5', '#7681cb', '#7787d0', '#788dd6',
              '#7993dc', '#7a99e2', '#7b9fe7', '#7ca6ed', '#7cacf3']
wdiv0_list = ['#760029', '#7b032d', '#800731', '#860b35', '#8b0e39', '#90123d',
              '#951641', '#9b1945', '#a01d49', '#a5204d', '#aa2451', '#af2755',
              '#b52b59', '#ba2e5d', '#bf3261', '#c43665', '#c93969', '#ce3d6d',
              '#d34172', '#d64777', '#d94d7c', '#dc5282', '#df5887', '#e15d8c',
              '#e46391', '#e76896', '#ea6d9a', '#ec739f', '#ef78a4', '#f27da9',
              '#f482ae', '#f787b2', '#fa8db7', '#fc92bc', '#ff97c0', '#fe9ec4',
              '#fea5c8', '#fdabcc', '#fcb2d0', '#fbb8d3', '#fbbfd7', '#fac5da',
              '#f9cbde', '#f9d1e1', '#f8d7e4', '#f8dde8', '#f7e3eb', '#f6e9ee',
              '#f6eff2', '#f5f5f5', '#eaf2f6', '#dfeff7', '#d4ecf8', '#c8e9f8',
              '#bde6f9', '#b1e3fa', '#a4dffb', '#98dcfc', '#8bd9fd', '#7ed5fe',
              '#72d1fe', '#6dcdfa', '#67c9f7', '#61c5f3', '#5bc1ef', '#55bcec',
              '#4fb8e8', '#49b4e4', '#44b0e1', '#3eacdd', '#38a8d9', '#32a3d6',
              '#2c9fd2', '#269bce', '#2097cb', '#1b93c7', '#158ec3', '#0f8abf',
              '#0986bc', '#0382b8', '#007eb4', '#0079af', '#0075ab', '#0071a6',
              '#006da1', '#00699d', '#006599', '#006194', '#005d90', '#00598b',
              '#005587', '#005183', '#004d7e', '#00497a', '#004576', '#004272',
              '#003e6e', '#003a69', '#003665']
wdiv1_list = ['#0017ab', '#061cb0', '#0d20b6', '#1325bb', '#1929c0', '#1e2dc4',
              '#2431c9', '#2935ce', '#2f39d2', '#343dd7', '#3a40db', '#3f44e0',
              '#4548e4', '#4a4ce9', '#4f50ed', '#5453f2', '#5a57f6', '#5f5bfa',
              '#645fff', '#6a63ff', '#7068ff', '#766dff', '#7c72ff', '#8277ff',
              '#877bff', '#8d80ff', '#9384ff', '#9889ff', '#9e8dff', '#a392ff',
              '#a996ff', '#ae9bff', '#b49fff', '#b9a4ff', '#bfa8ff', '#c4adff',
              '#c9b2ff', '#ccb7fe', '#cfbcfd', '#d3c1fc', '#d6c6fc', '#daccfb',
              '#ddd1fa', '#e1d6f9', '#e4dbf9', '#e7e0f8', '#ebe5f7', '#eeebf6',
              '#f2f0f6', '#f5f5f5', '#f6eff2', '#f6e9ee', '#f7e3eb', '#f8dde8',
              '#f8d7e4', '#f9d1e1', '#f9cbde', '#fac5da', '#fbbfd7', '#fbb8d3',
              '#fcb2d0', '#fdabcc', '#fea5c8', '#fe9ec4', '#ff97c0', '#fc92bc',
              '#fa8db7', '#f787b2', '#f482ae', '#f27da9', '#ef78a4', '#ec739f',
              '#ea6d9a', '#e76896', '#e46391', '#e15d8c', '#df5887', '#dc5282',
              '#d94d7c', '#d64777', '#d34172', '#ce3d6d', '#c93969', '#c43665',
              '#bf3261', '#ba2e5d', '#b52b59', '#af2755', '#aa2451', '#a5204d',
              '#a01d49', '#9b1945', '#951641', '#90123d', '#8b0e39', '#860b35',
              '#800731', '#7b032d', '#760029']
wdiv2_list = ['#870000', '#8d0201', '#930303', '#990504', '#9f0606', '#a50807',
              '#ab0a09', '#b10b0a', '#b70d0c', '#bd0f0d', '#c3100f', '#ca1211',
              '#d01412', '#d61514', '#dd1715', '#e31917', '#ea1b19', '#ed2721',
              '#ef3229', '#f13b30', '#f34436', '#f44d3c', '#f65442', '#f75c47',
              '#f8634c', '#fa6951', '#fb7056', '#fc765a', '#fe7d5f', '#ff8363',
              '#ff896b', '#fe9073', '#fd977c', '#fd9d84', '#fca38c', '#fca993',
              '#fbaf9b', '#fbb4a2', '#fabaa9', '#fac0b1', '#f9c5b8', '#f9cbbf',
              '#f8d0c6', '#f8d6cd', '#f7dbd3', '#f7e0da', '#f6e5e1', '#f6ebe8',
              '#f5f0ee', '#f5f5f5', '#e9f2f6', '#ddf0f7', '#d0edf8', '#c3eaf8',
              '#b6e7f9', '#a8e4fa', '#9ae1fb', '#8cdefc', '#7ddbfd', '#6dd7fe',
              '#62d3fd', '#5dcff9', '#58cbf4', '#53c7f0', '#4ec2ec', '#49bee8',
              '#43bae3', '#3eb6df', '#39b2db', '#34add7', '#2fa9d3', '#2aa5ce',
              '#25a1ca', '#209dc6', '#1b98c2', '#1594be', '#1090ba', '#0b8cb5',
              '#0688b1', '#0183ad', '#007fa9', '#007ba4', '#0077a0', '#00739b',
              '#006f97', '#006b93', '#00678e', '#00638a', '#005f86', '#005b81',
              '#00577d', '#005379', '#004f75', '#004b71', '#00476d', '#004369',
              '#003f65', '#003c61', '#00385d']
wdiv3_list = ['#fe9e74', '#fea076', '#fea178', '#ffa37a', '#ffa47c', '#ffa67e',
              '#ffa780', '#ffa983', '#ffaa85', '#ffac87', '#ffad89', '#ffaf8b',
              '#ffb08d', '#ffb28f', '#ffb391', '#ffb593', '#ffb796', '#ffb898',
              '#ffba9a', '#ffbb9c', '#ffbd9e', '#ffbea0', '#ffc0a2', '#ffc1a4',
              '#ffc3a7', '#ffc4a9', '#ffc6ab', '#ffc7ad', '#ffc9af', '#ffcab1',
              '#ffccb4', '#ffcdb6', '#ffcfb8', '#ffd0ba', '#ffd2bc', '#ffd3be',
              '#ffd5c1', '#ffd6c3', '#ffd8c5', '#ffd9c7', '#ffdbc9', '#ffdccc',
              '#ffdece', '#ffdfd0', '#ffe1d2', '#ffe2d4', '#ffe4d7', '#ffe5d9',
              '#ffe7db', '#ffe8dd', '#ffeadf', '#ffebe2', '#ffede4', '#ffeee6',
              '#fff0e8', '#fff1eb', '#fff3ed', '#fff4ef', '#fff6f1', '#fff7f4',
              '#fff9f6', '#fffaf8', '#fffcfa', '#fffdfd', '#fdfefe', '#fafdfe',
              '#f8fcfd', '#f6fbfd', '#f3fbfc', '#f1fafc', '#eef9fb', '#ecf8fa',
              '#eaf7fa', '#e7f6f9', '#e5f5f9', '#e2f4f8', '#e0f4f7', '#ddf3f7',
              '#dbf2f6', '#d9f1f6', '#d6f0f5', '#d4eff5', '#d1eef4', '#cfedf3',
              '#ccecf3', '#caecf2', '#c7ebf2', '#c5eaf1', '#c2e9f1', '#c0e8f0',
              '#bde7ef', '#bbe6ef', '#b8e5ee', '#b5e4ee', '#b3e4ed', '#b0e3ed',
              '#aee2ec', '#abe1eb', '#a8e0eb', '#a6dfea', '#a3deea', '#a0dde9',
              '#9ddce8', '#9bdbe8', '#98dbe7', '#95dae7', '#92d9e6', '#8fd8e6',
              '#8cd7e5', '#89d6e4', '#86d5e4', '#83d4e3', '#80d3e3', '#7dd3e2',
              '#7ad2e2', '#77d1e1', '#74d0e0', '#70cfe0', '#6dcedf', '#69cddf',
              '#66ccde', '#62cbde', '#5ecadd', '#5ac9dc', '#56c9dc', '#52c8db',
              '#4ec7db', '#49c6da']
wdiv4_list = ['#bb434f', '#bd4650', '#bf4951', '#c14c52', '#c34f54', '#c55255',
              '#c75556', '#c95858', '#cb5b59', '#cd5e5b', '#cf615c', '#d1645e',
              '#d36760', '#d56961', '#d76c63', '#d86f65', '#da7267', '#dc7569',
              '#dd786b', '#df7b6d', '#e17e6f', '#e28071', '#e48373', '#e68675',
              '#e78977', '#e98c7a', '#ea8f7c', '#eb927e', '#ed9581', '#ee9783',
              '#ef9a86', '#f19d89', '#f2a08b', '#f3a38e', '#f4a691', '#f6a994',
              '#f7ac97', '#f8af9a', '#f9b29d', '#fab4a0', '#fbb7a3', '#fbbaa6',
              '#fcbda9', '#fdc0ad', '#fec3b0', '#fec6b3', '#ffc9b7', '#ffccba',
              '#ffcfbe', '#ffd2c1', '#ffd5c5', '#ffd8c9', '#ffdbcd', '#ffded1',
              '#ffe1d5', '#ffe4d9', '#ffe7dd', '#ffeae1', '#ffede5', '#fff0e9',
              '#fff3ed', '#fff6f2', '#fff9f6', '#fffcfa', '#fafdfe', '#f6fbfd',
              '#f1fafb', '#ecf8fa', '#e8f6f9', '#e3f4f8', '#dff2f6', '#daf1f5',
              '#d6eff4', '#d1edf3', '#cdebf1', '#c8e9f0', '#c4e7ef', '#c0e5ed',
              '#bbe3ec', '#b7e2ea', '#b3e0e9', '#afdee7', '#abdce6', '#a6dae5',
              '#a2d8e3', '#9ed6e2', '#9ad4e0', '#96d2de', '#92d0dd', '#8ecedb',
              '#8accda', '#86cad8', '#82c8d7', '#7fc6d5', '#7bc4d3', '#77c2d2',
              '#73c0d0', '#6fbece', '#6cbccd', '#68bacb', '#64b8c9', '#61b6c7',
              '#5db3c6', '#59b1c4', '#56afc2', '#52adc0', '#4fabbf', '#4ba9bd',
              '#47a7bb', '#44a5b9', '#40a3b7', '#3da1b5', '#3a9fb4', '#369db2',
              '#339ab0', '#2f98ae', '#2c96ac', '#2894aa', '#2592a8', '#2190a6',
              '#1d8ea4', '#1a8ca2', '#1689a0', '#12879e', '#0d859c', '#09839a',
              '#048198', '#007f96']

vabcb = mpl_c.LinearSegmentedColormap.from_list( 'vabcb', vabcb_list )
vabcb_r = mpl_c.LinearSegmentedColormap.from_list( 'vabcb_r', vabcb_list[::-1] )

wdiv0 = mpl_c.LinearSegmentedColormap.from_list( 'wdiv0', wdiv0_list )
wdiv0_r = mpl_c.LinearSegmentedColormap.from_list( 'wdiv0_r', wdiv0_list[::-1] )
wdiv1 = mpl_c.LinearSegmentedColormap.from_list( 'wdiv1', wdiv1_list )
wdiv1_r = mpl_c.LinearSegmentedColormap.from_list( 'wdiv1_r', wdiv1_list[::-1] )
wdiv2 = mpl_c.LinearSegmentedColormap.from_list( 'wdiv2', wdiv2_list )
wdiv2_r = mpl_c.LinearSegmentedColormap.from_list( 'wdiv2_r', wdiv2_list[::-1] )
wdiv3 = mpl_c.LinearSegmentedColormap.from_list( 'wdiv3', wdiv3_list )
wdiv3_r = mpl_c.LinearSegmentedColormap.from_list( 'wdiv3_r', wdiv3_list[::-1] )
wdiv4 = mpl_c.LinearSegmentedColormap.from_list( 'wdiv4', wdiv4_list )
wdiv4_r = mpl_c.LinearSegmentedColormap.from_list( 'wdiv4_r', wdiv4_list[::-1] )

bdiv0_list = \
['#fcdc64', '#fcd664', '#fcd163', '#fbcc62', '#fbc662', '#fac161', '#f8bc5f',
 '#f7b75e', '#f5b25d', '#f4ad5c', '#f2a85a', '#f0a359', '#ed9e57', '#eb9a55',
 '#e89554', '#e69152', '#e38c50', '#e0884e', '#dd834d', '#d97f4b', '#d67b49',
 '#d37747', '#cf7345', '#cb6f43', '#c86b42', '#c46740', '#c0643e', '#bc603c',
 '#b85c3a', '#b35939', '#af5537', '#ab5235', '#a64f33', '#a24c32', '#9d4830',
 '#99452e', '#94422d', '#90402b', '#8b3d29', '#863a28', '#813726', '#7c3525',
 '#783223', '#733022', '#6e2d20', '#692b1f', '#64291d', '#5f271c', '#5a251b',
 '#552319', '#502118', '#4b1f17', '#461d16', '#401b14', '#3b1913', '#361812',
 '#311610', '#2d140e', '#28120c', '#23100a', '#1f0e08', '#1a0b06', '#140704',
 '#0b0302', '#000000', '#060408', '#0c080f', '#110d14', '#151019', '#18131d',
 '#1b1621', '#1e1826', '#211a2a', '#241d2e', '#271f33', '#292237', '#2c243c',
 '#2f2740', '#322944', '#352c49', '#382f4d', '#3b3252', '#3d3556', '#40385b',
 '#433a5f', '#453e64', '#484168', '#4b446d', '#4d4771', '#504a75', '#524d7a',
 '#54517e', '#575482', '#595786', '#5b5b8a', '#5d5e8f', '#606293', '#626697',
 '#64699a', '#666d9e', '#6871a2', '#6974a6', '#6b78a9', '#6d7cad', '#6f80b0',
 '#7084b4', '#7288b7', '#738cba', '#7490bd', '#7694c0', '#7799c2', '#789dc5',
 '#79a1c7', '#7aa6c9', '#7baacb', '#7baecd', '#7cb3cf', '#7db7d0', '#7dbcd1',
 '#7dc1d2', '#7dc5d3', '#7dcad3', '#7dcfd3', '#7dd4d3', '#7cd9d2', '#7bded1',
 '#7ae3cf', '#79e8cd', '#77edca']

bdiv1_list = \
['#fcdc64', '#fcd764', '#fbd163', '#fbcc63', '#fbc663', '#fbc162', '#fabb62',
 '#fab562', '#fab061', '#faaa61', '#f9a461', '#f99e60', '#f99860', '#f8925f',
 '#f88b5f', '#f5875d', '#f2825a', '#ef7e57', '#ec7955', '#e87552', '#e5704f',
 '#e26c4c', '#df684a', '#db6347', '#d85f44', '#d55a41', '#d1563e', '#ce513c',
 '#cb4c39', '#c74836', '#c44333', '#c03e30', '#bd3a2d', '#b9352a', '#b53027',
 '#b22b24', '#ac2923', '#a62821', '#a02720', '#9a251f', '#94241e', '#8e221d',
 '#88211b', '#821f1a', '#7c1e19', '#771d18', '#711b17', '#6b1a16', '#661915',
 '#601713', '#5b1612', '#551511', '#501310', '#4a120f', '#45110e', '#400f0d',
 '#3b0e0c', '#360d0b', '#300c0a', '#2b0a09', '#250908', '#1f0706', '#170505',
 '#0c0303', '#000000', '#060408', '#0c0811', '#110c18', '#160f1e', '#1a1123',
 '#1d1428', '#20162c', '#231830', '#271a35', '#2a1c39', '#2d1f3e', '#312143',
 '#342347', '#38264c', '#3b2851', '#3f2b56', '#422d5b', '#462f5f', '#493264',
 '#4d3469', '#51376e', '#543973', '#583c79', '#5c3e7e', '#604183', '#644488',
 '#67468d', '#6b4993', '#6d4c97', '#6e519b', '#6f55a0', '#6f59a4', '#705ea8',
 '#7162ac', '#7166b0', '#726ab4', '#726fb8', '#7373bc', '#7477c0', '#747bc4',
 '#757fc8', '#7684cc', '#7688d0', '#778cd4', '#7790d8', '#7894dc', '#7999e0',
 '#799de4', '#7aa1e8', '#7aa5ec', '#7baaf0', '#7bafed', '#7ab5e9', '#7abae7',
 '#7abfe4', '#79c5e1', '#79cade', '#79cfdb', '#78d4d8', '#78d9d5', '#78ded2',
 '#78e3d0', '#77e8cd', '#77edca']

bdiv2_list = \
['#7ed9e1', '#7bd6df', '#78d3dc', '#76d0da', '#73cdd7', '#70cad5', '#6ec7d2',
 '#6bc3d0', '#68c0cd', '#65bdcb', '#63bac8', '#60b7c6', '#5db4c4', '#5bb1c1',
 '#58aebf', '#55abbc', '#53a8ba', '#50a5b8', '#4da2b5', '#4b9fb3', '#489cb1',
 '#459aae', '#4497ab', '#4394a8', '#4291a5', '#418ea1', '#418b9e', '#40889b',
 '#3f8597', '#3e8294', '#3e7f91', '#3d7c8d', '#3c798a', '#3b7687', '#3b7384',
 '#3a7080', '#396d7d', '#396a7a', '#386877', '#376574', '#366271', '#365f6d',
 '#355c6a', '#345967', '#345764', '#335461', '#32515e', '#314e5b', '#314c58',
 '#304955', '#2f4652', '#2f434f', '#2e414c', '#2d3e49', '#2d3b46', '#2c3943',
 '#2b3640', '#2b333d', '#2a313a', '#292e37', '#292c34', '#282931', '#27262e',
 '#27242b', '#262128', '#2c2129', '#33222a', '#38222c', '#3e222d', '#43222e',
 '#49232f', '#4e2330', '#532331', '#582332', '#5c2433', '#612433', '#662434',
 '#6b2435', '#6f2536', '#742537', '#792538', '#7d2539', '#82253a', '#86263b',
 '#8b263c', '#90263c', '#94263d', '#99273e', '#9d273f', '#a22740', '#a52a41',
 '#a72d42', '#aa3143', '#ac3444', '#af3745', '#b13a47', '#b43d48', '#b64049',
 '#b9434a', '#bb464b', '#bd494c', '#c04c4d', '#c24f4e', '#c5524f', '#c75550',
 '#c95851', '#cc5b52', '#ce5e53', '#d06154', '#d36455', '#d56756', '#d76a57',
 '#da6c58', '#dc6f59', '#de725a', '#e1755b', '#e3785c', '#e57b5d', '#e87e5e',
 '#ea815f', '#ec8460', '#ef8761', '#f18a62', '#f38c63', '#f68f64', '#f89265',
 '#fa9566', '#fd9867', '#ff9b68']

bdiv0 = mpl_c.LinearSegmentedColormap.from_list( 'bdiv0', bdiv0_list )
bdiv0_r = mpl_c.LinearSegmentedColormap.from_list( 'bdiv0_r', bdiv0_list[::-1] )
bdiv1 = mpl_c.LinearSegmentedColormap.from_list( 'bdiv1', bdiv1_list )
bdiv1_r = mpl_c.LinearSegmentedColormap.from_list( 'bdiv1_r', bdiv1_list[::-1] )
bdiv2 = mpl_c.LinearSegmentedColormap.from_list( 'bdiv2', bdiv2_list )
bdiv2_r = mpl_c.LinearSegmentedColormap.from_list( 'bdiv2_r', bdiv2_list[::-1] )

RdBuMod_list = \
['#610524', '#650827', '#690c2a', '#6c0f2d', '#701330', '#731633', '#771a36',
 '#7a1d39', '#7e203b', '#81243e', '#842741', '#882a44', '#8b2e46', '#8e3149',
 '#92344c', '#95374e', '#983b51', '#9c3e54', '#9f4156', '#a24459', '#a5485c',
 '#a94b5e', '#ac4e61', '#af5164', '#b35467', '#b65869', '#b95b6c', '#bc5f70',
 '#bf6273', '#c26576', '#c5697a', '#c86c7d', '#cb7080', '#ce7384', '#d17787',
 '#d47a8b', '#d77e8e', '#da8191', '#dd8495', '#e08898', '#e38b9c', '#e68f9f',
 '#e992a2', '#ec96a6', '#ef99a9', '#f29dad', '#f5a0b0', '#f9a4b4', '#fca8b7',
 '#ffabbb', '#feb0bf', '#feb5c3', '#fdbbc7', '#fcc0cb', '#fcc5cf', '#fbcad3',
 '#facfd7', '#fad4db', '#f9d8de', '#f8dde2', '#f8e2e6', '#f7e7ea', '#f6ecee',
 '#f6f0f1', '#ecf3f3', '#e3f1f1', '#daefef', '#d1edec', '#c7ebea', '#bee9e8',
 '#b4e7e6', '#abe5e3', '#a0e3e1', '#96e1df', '#8cdedc', '#81dcda', '#76dad7',
 '#70d7d4', '#6cd4d1', '#67d0ce', '#63cdca', '#5ecac7', '#5ac7c4', '#56c3c1',
 '#51c0be', '#4dbdbb', '#48bab7', '#44b7b4', '#40b3b1', '#3bb0ae', '#37adab',
 '#32aaa8', '#2ea7a4', '#29a3a1', '#25a09e', '#219d9b', '#1c9a98', '#189694',
 '#139391', '#0f908e', '#0b8d8b', '#068988', '#028685', '#008381', '#00807e',
 '#007c7b', '#007978', '#007675', '#007372', '#00706e', '#006c6b', '#006968',
 '#006665', '#006362', '#00605f', '#005d5c', '#005a59', '#005756', '#005453',
 '#005150', '#004d4d', '#004b4a', '#004847', '#004545', '#004242', '#003f3f',
 '#003c3c', '#003939']
AquaIndigo_list = \
['#003a2c', '#003d2f', '#004031', '#004334', '#004637', '#00493a', '#004c3d',
 '#004f3f', '#005242', '#005545', '#005948', '#005c4b', '#005f4e', '#006251',
 '#006554', '#006857', '#006c5a', '#006f5d', '#007260', '#007563', '#007966',
 '#007c69', '#007f6c', '#00836f', '#008672', '#028975', '#068c79', '#0a907c',
 '#0e937f', '#129682', '#169a85', '#1a9d89', '#1ea08c', '#22a48f', '#26a792',
 '#2aaa95', '#2eae99', '#32b19c', '#36b49f', '#3ab8a2', '#3ebba5', '#42bea9',
 '#46c2ac', '#4ac5af', '#4ec8b2', '#52ccb5', '#56cfb9', '#5ad2bc', '#5ed6bf',
 '#63d9c2', '#68dcc6', '#74dfca', '#81e1ce', '#8ce3d2', '#98e5d6', '#a3e7da',
 '#aee9dd', '#b9ebe1', '#c3ece4', '#ceeee8', '#d8f0eb', '#e2f2ef', '#ebf3f2',
 '#f5f5f5', '#f5f0f6', '#f5ebf6', '#f5e6f7', '#f4e1f8', '#f4dcf8', '#f4d7f9',
 '#f4d1fa', '#f4ccfb', '#f4c7fb', '#f4c1fc', '#f3bcfd', '#f3b7fe', '#f3b1fe',
 '#f3abff', '#efa8fd', '#eba4fa', '#e7a1f8', '#e49ef6', '#e09af3', '#dc97f1',
 '#d993ef', '#d590ec', '#d18cea', '#cd89e8', '#ca85e6', '#c682e3', '#c27fe1',
 '#bf7bdf', '#bb78dd', '#b774da', '#b471d8', '#b06ed6', '#ac6ad4', '#a967d1',
 '#a564cf', '#a160cd', '#9e5dcb', '#9a5ac8', '#9756c5', '#9453c2', '#9050bf',
 '#8d4dbb', '#8a49b8', '#8746b5', '#8343b2', '#8040ae', '#7d3cab', '#7a39a8',
 '#7636a5', '#7333a1', '#702f9e', '#6c2c9b', '#692998', '#662694', '#632291',
 '#5f1f8e', '#5c1c8a', '#581887', '#551584', '#521180', '#4e0e7d', '#4b0b79',
 '#470776']
NavyOrangeRed_list = \
['#00228d', '#042591', '#092895', '#0d2b98', '#122e9c', '#16319f', '#1b34a3',
 '#1f36a6', '#2339aa', '#273cad', '#2c3fb1', '#3042b4', '#3445b8', '#3847bb',
 '#3c4abf', '#414dc2', '#4550c5', '#4953c9', '#4d56cc', '#5158d0', '#555bd3',
 '#5a5ed7', '#5e61da', '#6264dd', '#6666e1', '#6a6ae3', '#6e6de5', '#7270e6',
 '#7674e7', '#7a77e8', '#7e7bea', '#827eeb', '#8682ec', '#8a85ed', '#8e89ee',
 '#928cf0', '#9690f1', '#9993f2', '#9d97f3', '#a19af4', '#a59df6', '#a9a1f7',
 '#ada4f8', '#b1a8f9', '#b5abfa', '#b9affc', '#bdb2fd', '#c1b6fe', '#c5b9ff',
 '#c8bdfe', '#cbc1fe', '#cec5fd', '#d1c9fc', '#d5cdfc', '#d8d1fb', '#dbd5fa',
 '#ded9fa', '#e2ddf9', '#e5e1f8', '#e8e5f8', '#ebe9f7', '#efedf6', '#f2f1f6',
 '#f5f5f5', '#f5f1ef', '#f6ede8', '#f6e9e2', '#f6e5db', '#f7e1d5', '#f7ddce',
 '#f8d9c8', '#f8d5c1', '#f8d1ba', '#f9cdb3', '#f9c8ad', '#fac4a6', '#fac09f',
 '#fabb98', '#fbb791', '#fbb38a', '#fcae82', '#fcaa7b', '#fda573', '#fda06c',
 '#fd9b64', '#fe965c', '#fe9154', '#ff8c4b', '#fe8746', '#fd8342', '#fc7e3f',
 '#fb793b', '#f97538', '#f87034', '#f76b30', '#f5662d', '#f46129', '#f35c25',
 '#f15621', '#f0511d', '#ee4b18', '#ec4514', '#eb3e0f', '#e9380a', '#e73104',
 '#e42a00', '#e02800', '#db2600', '#d62400', '#d22200', '#cd2000', '#c81e00',
 '#c31c00', '#bf1a00', '#ba1800', '#b61600', '#b11400', '#ac1200', '#a81000',
 '#a30e00', '#9e0c00', '#9a0a00', '#950800', '#910600', '#8c0400', '#880200',
 '#840000']
cm6BuOr_list = \
['#003387', '#00368b', '#00398e', '#003c92', '#003f95', '#004299', '#00459c',
 '#0048a0', '#004ba3', '#004ea7', '#0051aa', '#0054ae', '#0057b1', '#005ab5',
 '#005db9', '#0060bc', '#0063c0', '#0066c4', '#0069c7', '#006ccb', '#006fcf',
 '#0072d2', '#0075d6', '#0078da', '#027cdd', '#077fde', '#0c83e0', '#1186e1',
 '#168ae3', '#1b8de4', '#2090e6', '#2594e7', '#2a97e8', '#2f9aea', '#349eeb',
 '#39a1ed', '#3ea4ee', '#42a8f0', '#47abf1', '#4caef2', '#51b2f4', '#55b5f5',
 '#5ab8f7', '#5fbbf8', '#64bef9', '#68c2fb', '#6dc5fc', '#72c8fe', '#76cbff',
 '#7fcefe', '#87d1fe', '#90d4fd', '#98d7fc', '#a0d9fc', '#a9dcfb', '#b1defa',
 '#b8e1fa', '#c0e4f9', '#c8e6f9', '#d0e9f8', '#d7ebf7', '#dfeef7', '#e6f0f6',
 '#eef3f6', '#f5f5f5', '#f6f2e5', '#f6eed6', '#f7ebc6', '#f7e7b5', '#f8e3a4',
 '#f8df92', '#f9db80', '#fad76e', '#fad35a', '#fbce46', '#fcca31', '#fdc51b',
 '#fdc004', '#fabc00', '#f7b900', '#f3b600', '#efb200', '#ebaf00', '#e7ac00',
 '#e4a900', '#e0a600', '#dca300', '#d89f00', '#d59c00', '#d19900', '#cd9600',
 '#c99300', '#c69000', '#c28d00', '#be8a00', '#bb8600', '#b78300', '#b48000',
 '#b07d00', '#ac7a00', '#a97700', '#a57400', '#a27100', '#9e6e00', '#9b6b00',
 '#986800', '#946500', '#916200', '#8e5f00', '#8a5c00', '#875900', '#845600',
 '#815300', '#7d5100', '#7a4e00', '#774b00', '#744800', '#714500', '#6e4200',
 '#6a3f00', '#673d00', '#643a00', '#613700', '#5e3400', '#5b3100', '#582f00',
 '#552c00', '#522900', '#4f2600']
RdBuX_list = \
['#840000', '#880200', '#8c0400', '#910600', '#950800', '#9a0a00', '#9e0b00',
 '#a30d00', '#a70f00', '#ac1100', '#b01300', '#b51500', '#b91700', '#be1900',
 '#c21b00', '#c71d00', '#cc1f00', '#d02100', '#d52300', '#da2500', '#de2800',
 '#e32a00', '#e62e02', '#e83508', '#ea3c0d', '#ec4212', '#ed4816', '#ef4e1b',
 '#f0541f', '#f25923', '#f35e27', '#f5632b', '#f6682f', '#f76d32', '#f97236',
 '#fa773a', '#fb7b3d', '#fc8040', '#fd8544', '#ff8947', '#ff8e4e', '#fe9356',
 '#fe985f', '#fd9d66', '#fda26e', '#fca676', '#fcab7d', '#fcaf84', '#fbb48b',
 '#fbb892', '#fabc99', '#fac1a0', '#fac5a7', '#f9c9ae', '#f9cdb5', '#f8d1bb',
 '#f8d5c2', '#f8d9c8', '#f7ddcf', '#f7e1d5', '#f6e5dc', '#f6e9e2', '#f6ede8',
 '#f5f1ef', '#f5f5f5', '#edf3f6', '#e5f0f6', '#dceef7', '#d4ecf8', '#cbe9f8',
 '#c3e7f9', '#bae5fa', '#b1e2fa', '#a8e0fb', '#9fddfc', '#96dafc', '#8cd8fd',
 '#82d5fe', '#79d2ff', '#71cffe', '#6dccfb', '#68c9f9', '#64c6f7', '#5fc2f4',
 '#5bbff2', '#56bcef', '#52b9ed', '#4db6ea', '#49b2e8', '#44afe6', '#40ace3',
 '#3ba9e1', '#37a5de', '#32a2dc', '#2e9fd9', '#299cd7', '#2499d5', '#2095d2',
 '#1b92d0', '#178fcd', '#128bcb', '#0e88c8', '#0985c6', '#0482c3', '#007ec1',
 '#007bbd', '#0078b9', '#0075b6', '#0072b2', '#006eaf', '#006bab', '#0068a8',
 '#0065a4', '#0062a1', '#005f9d', '#005c9a', '#005997', '#005693', '#005390',
 '#00508c', '#004d89', '#004a86', '#004782', '#00447f', '#00417c', '#003e79',
 '#003b75', '#003972', '#00366f']

RdBuMod = mpl_c.LinearSegmentedColormap.from_list( 'RdBuMod', RdBuMod_list )
RdBuMod_r = mpl_c.LinearSegmentedColormap.from_list( 'RdBuMod_r', RdBuMod_list[::-1] )
AquaIndigo = mpl_c.LinearSegmentedColormap.from_list( 'AquaIndigo', AquaIndigo_list )
AquaIndigo_r = mpl_c.LinearSegmentedColormap.from_list( 'AquaIndigo_r', AquaIndigo_list[::-1] )
NavyOrangeRed = mpl_c.LinearSegmentedColormap.from_list( 'NavyOrangeRed', NavyOrangeRed_list )
NavyOrangeRed_r = mpl_c.LinearSegmentedColormap.from_list( 'NavyOrangeRed_r', NavyOrangeRed_list[::-1] )
cm6BuOr = mpl_c.LinearSegmentedColormap.from_list( 'cm6BuOr', cm6BuOr_list )
cm6BuOr_r = mpl_c.LinearSegmentedColormap.from_list( 'cm6BuOr_r', cm6BuOr_list[::-1] )
RdBuX = mpl_c.LinearSegmentedColormap.from_list( 'RdBuX', RdBuX_list )
RdBuX_r = mpl_c.LinearSegmentedColormap.from_list( 'RdBuX_r', RdBuX_list[::-1] )

NavyOrangeRed_BL_list = \
['#6440cc', '#6340c9', '#6340c6', '#623fc4', '#613fc1', '#603fbe', '#5f3ebb',
 '#5f3eb8', '#5e3db5', '#5d3db3', '#5c3db0', '#5b3cad', '#5a3caa', '#5a3ca7',
 '#593ba5', '#583ba2', '#573b9f', '#563a9c', '#553a9a', '#543997', '#543994',
 '#533991', '#52388f', '#51388c', '#503789', '#4f3787', '#4e3784', '#4d3681',
 '#4c367f', '#4b357c', '#4a3579', '#493577', '#483474', '#473471', '#46336f',
 '#46336c', '#45336a', '#443267', '#433264', '#423162', '#41315f', '#40305d',
 '#3e305a', '#3d3058', '#3c2f55', '#3b2f53', '#3a2e50', '#392e4e', '#382d4b',
 '#372d49', '#362c47', '#352c44', '#342b42', '#332b3f', '#322b3d', '#302a3b',
 '#2f2a38', '#2e2936', '#2d2933', '#2c2831', '#2b282f', '#29272d', '#28272a',
 '#272628', '#282625', '#2b2625', '#2e2725', '#302724', '#332724', '#352724',
 '#382723', '#3a2823', '#3d2822', '#3f2822', '#422822', '#442821', '#462821',
 '#492920', '#4b2920', '#4d2920', '#50291f', '#52291f', '#54291e', '#57291e',
 '#59291e', '#5b291d', '#5d291d', '#60291c', '#62291c', '#64291b', '#67291b',
 '#69281a', '#6b281a', '#6e2819', '#702819', '#722818', '#742718', '#772717',
 '#792717', '#7b2616', '#7e2616', '#802615', '#822515', '#852514', '#872413',
 '#892413', '#8b2312', '#8e2211', '#902211', '#922110', '#95200f', '#97200f',
 '#991f0e', '#9c1e0d', '#9e1d0c', '#a01c0b', '#a31a0a', '#a5190a', '#a81809',
 '#aa1608', '#ac1407', '#af1206', '#b11005', '#b30e04', '#b60b03', '#b80702',
 '#bb0401', '#bd0000']

NavyOrangeRed_BL_full_list = \
['#886ffb', '#866df7', '#846cf2', '#826aee', '#8068ea', '#7e66e5', '#7b64e1',
 '#7963dd', '#7761d8', '#755fd4', '#735dd0', '#715ccb', '#6e5ac7', '#6c58c3',
 '#6a56bf', '#6855ba', '#6653b6', '#6451b2', '#624fae', '#604eaa', '#5e4ca6',
 '#5c4aa1', '#59499d', '#574799', '#554595', '#534491', '#51428d', '#4f4089',
 '#4d3f85', '#4b3d81', '#493b7d', '#473a79', '#453876', '#433772', '#41356e',
 '#3f336a', '#3d3266', '#3b3063', '#392f5f', '#372d5b', '#352b57', '#332a54',
 '#312850', '#30274d', '#2e2549', '#2c2445', '#2a2242', '#28213e', '#261f3b',
 '#241e37', '#221c34', '#201b31', '#1f192d', '#1d182a', '#1b1627', '#191524',
 '#171320', '#16121d', '#14101a', '#110d17', '#0e0b14', '#0b0810', '#07050b',
 '#040306', '#070201', '#0d0502', '#120703', '#160a04', '#1a0c05', '#1d0e06',
 '#201007', '#221209', '#25130a', '#28140b', '#2b150c', '#2e170d', '#31180d',
 '#35190e', '#381a0f', '#3b1b10', '#3e1c10', '#421e11', '#451f11', '#482012',
 '#4c2112', '#4f2213', '#532313', '#562514', '#5a2614', '#5d2715', '#612815',
 '#642915', '#682a16', '#6b2c16', '#6f2d17', '#722e17', '#762f17', '#7a3018',
 '#7d3118', '#813318', '#853419', '#883519', '#8c361a', '#90371a', '#94381a',
 '#983a1b', '#9b3b1b', '#9f3c1b', '#a33d1c', '#a73e1c', '#ab401c', '#af411d',
 '#b3421d', '#b6431d', '#ba441e', '#be451e', '#c2471e', '#c6481f', '#ca491f',
 '#ce4a1f', '#d24b1f', '#d64d20', '#da4e20', '#de4f20', '#e25021', '#e75121',
 '#eb5321', '#ef5421']

NORBL_list = \
['#d15417', '#cf5419', '#cd541a', '#cb541b', '#c9541c', '#c7541e', '#c5541f',
 '#c35420', '#c15421', '#bf5422', '#bd5423', '#bb5424', '#b95425', '#b75426',
 '#b55427', '#b35428', '#b15429', '#af5329', '#ad532a', '#ab532b', '#a9532c',
 '#a7532d', '#a5532e', '#a3532e', '#a1532f', '#9f5330', '#9d5231', '#9b5231',
 '#995232', '#975233', '#945234', '#925234', '#905235', '#8e5136', '#8c5137',
 '#8a5137', '#885138', '#865139', '#845039', '#82503a', '#80503b', '#7e503b',
 '#7c503c', '#7a4f3d', '#774f3d', '#754f3e', '#734f3f', '#714e3f', '#6f4e40',
 '#6d4e40', '#6a4e41', '#684d42', '#664d42', '#644d43', '#624d44', '#5f4c44',
 '#5d4c45', '#5b4c45', '#584b46', '#564b47', '#544b47', '#514a48', '#4f4a48',
 '#4c4a49', '#4a4a4c', '#4b4b4e', '#4c4b50', '#4d4c53', '#4e4c55', '#4f4d57',
 '#4f4d5a', '#504e5c', '#514e5e', '#524f60', '#535063', '#535065', '#545168',
 '#55516a', '#55526c', '#56526f', '#575371', '#585373', '#585476', '#595478',
 '#5a557b', '#5a567d', '#5b567f', '#5b5782', '#5c5784', '#5d5887', '#5d5889',
 '#5e598c', '#5e598e', '#5f5a90', '#605b93', '#605b95', '#615c98', '#615c9a',
 '#625d9d', '#625d9f', '#635ea2', '#635fa4', '#645fa7', '#6460a9', '#6460ac',
 '#6561ae', '#6561b1', '#6662b4', '#6662b6', '#6663b9', '#6764bb', '#6764be',
 '#6765c0', '#6865c3', '#6866c6', '#6866c8', '#6967cb', '#6968cd', '#6968d0',
 '#6a69d3', '#6a69d5', '#6a6ad8', '#6a6ada', '#6a6bdd', '#6b6ce0', '#6b6ce2',
 '#6b6de5', '#6b6de8']

NavyOrangeRed_BL = mpl_c.LinearSegmentedColormap.from_list( 'NavyOrangeRed_BL', NavyOrangeRed_BL_list )
NavyOrangeRed_BL_r = mpl_c.LinearSegmentedColormap.from_list( 'NavyOrangeRed_BL_r', NavyOrangeRed_BL_list[::-1] )
NavyOrangeRed_BL_full = mpl_c.LinearSegmentedColormap.from_list( 'NavyOrangeRed_BL_full', NavyOrangeRed_BL_full_list )
NavyOrangeRed_BL_full_r = mpl_c.LinearSegmentedColormap.from_list( 'NavyOrangeRed_BL_full_r', NavyOrangeRed_BL_full_list[::-1] )
NORBL = mpl_c.LinearSegmentedColormap.from_list( 'NORBL', NORBL_list )
NORBL_r = mpl_c.LinearSegmentedColormap.from_list( 'NORBL_r', NORBL_list[::-1] )

Cycl_wdiv4_list = [ (0.820, 0.369, 0.333),
                    (0.600, 0.420, 0.733),
                    (0.341, 0.729, 0.812),
                    (0.561, 0.702, 0.455),
                    (0.820, 0.369, 0.333) ]
Cycl_wdiv4 = mpl_c.LinearSegmentedColormap.from_list('Cycl_wdiv4', Cycl_wdiv4_list)
Cycl_wdiv4_r = mpl_c.LinearSegmentedColormap.from_list('Cycl_wdiv4_r', Cycl_wdiv4_list[::-1])

young_list = ['#3bfaff', '#3af5fe', '#38f1fe', '#37ecfd', '#36e7fc', '#35e2fc',
              '#34defb', '#33d9fa', '#32d4fa', '#31cff9', '#30cbf9', '#2ec6f8',
              '#2dc1f7', '#2cbcf7', '#2bb8f6', '#2ab3f5', '#29aef5', '#28aaf4',
              '#27a5f3', '#26a0f3', '#249bf2', '#2397f1', '#2292f1', '#218df0',
              '#2088ef', '#1f83ef', '#1e7fee', '#1d7aed', '#1b75ed', '#1a70ec',
              '#196beb', '#1866eb', '#1761ea', '#155be9', '#1456e9', '#1350e8',
              '#124be7', '#1045e6', '#0f3fe5', '#0d39e5', '#0c32e4', '#0a2ae3',
              '#0822e1', '#0618e0', '#020ade', '#0000d9', '#0000d0', '#0000c6',
              '#0000bd', '#0000b4', '#0000aa', '#0000a1', '#000098', '#000090',
              '#000087', '#00007e', '#000076', '#00006d', '#000065', '#00005c',
              '#000053', '#000048', '#00003b', '#000028', '#140003', '#200005',
              '#280006', '#2f0007', '#350008', '#3b0009', '#40000a', '#45000a',
              '#4b000b', '#50000c', '#56000d', '#5c000e', '#61000f', '#670010',
              '#6d0010', '#730011', '#790012', '#7f0013', '#850014', '#8b0015',
              '#910016', '#980017', '#9e0018', '#a40019', '#aa001a', '#b1001b',
              '#b7001c', '#be001d', '#c4001e', '#cb001f', '#d10020', '#d80021',
              '#df0022', '#e50023', '#ec0024', '#f30025', '#fa0026', '#ff0e24',
              '#ff2a1f', '#ff3b1d', '#ff471a', '#ff5219', '#ff5c17', '#ff6515',
              '#ff6d14', '#ff7513', '#ff7d11', '#ff8410', '#ff8b0f', '#ff920e',
              '#ff980d', '#ff9f0c', '#ffa50b', '#ffab0a', '#ffb109', '#ffb708',
              '#ffbd07', '#ffc306', '#ffc905', '#ffce04', '#ffd403', '#ffda02',
              '#ffdf01', '#ffe500']
BluePurpleRedor_list = ['#b9ffff', '#b9fdfe', '#bafbfe', '#bafafd', '#baf8fc',
                        '#bbf6fc', '#bbf4fb', '#bbf2fa', '#bbf0fa', '#bceef9',
                        '#bcedf8', '#bcebf8', '#bde9f7', '#bde7f6', '#bde5f6',
                        '#bee3f5', '#bee1f4', '#bedff4', '#bfddf3', '#bfdcf2',
                        '#bfdaf2', '#c0d8f1', '#c0d6f0', '#c0d4f0', '#c1d2ef',
                        '#c1d0ee', '#c1ceee', '#c2cced', '#c2caec', '#c2c9ec',
                        '#c3c6eb', '#c3c5ea', '#c3c3ea', '#c4c1e9', '#c4bfe8',
                        '#c4bde8', '#c5bbe7', '#c5b9e6', '#c5b7e5', '#c6b5e5',
                        '#c6b3e4', '#c6b1e3', '#c7afe3', '#c7ade2', '#c7abe1',
                        '#c8a9e0', '#c8a7e0', '#c8a4df', '#c9a2de', '#c9a0dd',
                        '#ca9edd', '#ca9cdc', '#ca9adb', '#cb98da', '#cb95da',
                        '#cb93d9', '#cc91d8', '#cc8fd7', '#cd8dd6', '#cd8ad6',
                        '#cd88d5', '#ce86d4', '#ce83d3', '#cf81d2', '#cf7ed1',
                        '#cf7cd1', '#d07ad0', '#d077cf', '#d075ce', '#d073cb',
                        '#cf72c8', '#cf70c5', '#ce6fc3', '#cd6dc0', '#cd6bbd',
                        '#cc6aba', '#cb68b8', '#cb67b5', '#ca65b2', '#ca64af',
                        '#c962ad', '#c860aa', '#c85fa7', '#c75da4', '#c65ca1',
                        '#c65a9f', '#c5589c', '#c45799', '#c45596', '#c35493',
                        '#c25290', '#c2508d', '#c14f8a', '#c04d87', '#c04b84',
                        '#bf4981', '#be487e', '#bd467b', '#bd4478', '#bc4275',
                        '#bb4172', '#bb3f6f', '#ba3d6b', '#b93b68', '#b83965',
                        '#b83762', '#b7365e', '#b6345b', '#b53257', '#b43054',
                        '#b42e50', '#b32c4d', '#b22949', '#b12745', '#b02541',
                        '#af233d', '#ae2039', '#ad1e35', '#ac1c30', '#ab192c',
                        '#aa1627', '#a91422', '#a8111d', '#a70e18', '#a50a12',
                        '#a4070c', '#a20306', '#a10000']
PrinsensvlagLinear_list = ['#ffff9a', '#fffd99', '#fffa98', '#fff898',
                           '#fff597', '#fff396', '#fff095', '#ffee95',
                           '#ffeb94', '#ffe993', '#ffe693', '#ffe492',
                           '#ffe191', '#ffde90', '#ffdc90', '#ffd98f',
                           '#ffd78e', '#ffd48e', '#ffd28d', '#ffcf8c',
                           '#ffcc8b', '#ffca8b', '#ffc78a', '#ffc589',
                           '#ffc288', '#ffbf88', '#ffbd87', '#ffba86',
                           '#ffb785', '#feb585', '#f9b485', '#f4b486',
                           '#f0b386', '#ebb387', '#e6b287', '#e1b188',
                           '#dcb189', '#d7b089', '#d2af8a', '#cdaf8a',
                           '#c7ae8b', '#c2ad8b', '#bdad8c', '#b8ac8d',
                           '#b2ab8d', '#acaa8e', '#a7aa8e', '#a1a98f',
                           '#9ba890', '#95a790', '#8fa791', '#89a692',
                           '#82a592', '#7ba493', '#75a394', '#6da295',
                           '#66a196', '#5fa096', '#579f97', '#4e9e98',
                           '#459d99', '#3c9c9a', '#329b9b', '#27999d',
                           '#1a979e', '#0d96a0', '#0094a1', '#0092a0',
                           '#0090a0', '#008e9f', '#008c9f', '#008a9f',
                           '#00889e', '#00869e', '#00849d', '#00829d',
                           '#00809c', '#007e9c', '#007c9b', '#007a9b',
                           '#00789a', '#00769a', '#007599', '#007399',
                           '#007198', '#006f98', '#006d98', '#006b97',
                           '#006997', '#006796', '#006596', '#006395',
                           '#006195', '#005f94', '#005d94', '#005b93',
                           '#005993', '#005792', '#005592', '#005392',
                           '#005291', '#005091', '#004e90', '#004c90',
                           '#004a8f', '#00488f', '#00468e', '#00448e',
                           '#00428d', '#00408d', '#003e8c', '#003c8c',
                           '#00398b', '#00378b', '#00358a', '#00338a',
                           '#003189', '#002f89', '#002d88', '#002b88',
                           '#002887', '#002687', '#002486', '#002186',
                           '#001f85', '#001c84', '#001984', '#001783']
nihit_list = ['#000300', '#000a0a', '#011113', '#01181d', '#021f27', '#022631',
              '#032e3a', '#033544', '#033c4e', '#044358', '#044a61', '#05516b',
              '#055875', '#065f7e', '#066688', '#066d92', '#07749c', '#077ba5',
              '#0883af', '#088ab9', '#0991c2', '#0998cc', '#0a9fd6', '#0aa6e0',
              '#0aade9', '#0bb4f3', '#0db4f3', '#0fafed', '#12aae7', '#15a4e0',
              '#179fda', '#1a9ad4', '#1d95cd', '#2090c7', '#228bc1', '#2585bb',
              '#2880b4', '#2b7bae', '#2d76a8', '#3071a1', '#336c9b', '#356795',
              '#38618e', '#3b5c88', '#3e5782', '#40527c', '#434d75', '#46486f',
              '#484269', '#4b3d62', '#4e385c', '#513456', '#563354', '#5c3251',
              '#61314f', '#66314c', '#6c304a', '#712f47', '#762e45', '#7c2d42',
              '#812c40', '#862c3d', '#8c2b3b', '#912a38', '#962936', '#9b2833',
              '#a12731', '#a6272e', '#ab262c', '#b12529', '#b62427', '#bb2324',
              '#c12222', '#c6221f', '#cb211d', '#d1201a', '#d61f18', '#d82217',
              '#d92517', '#db2917', '#dc2c16', '#dd3016', '#df3316', '#e03716',
              '#e13a16', '#e33e16', '#e44115', '#e54515', '#e74815', '#e84c15',
              '#e94f15', '#eb5315', '#ec5615', '#ed5a14', '#ef5d14', '#f06114',
              '#f26414', '#f36814', '#f46b14', '#f66f13', '#f77213', '#f87613',
              '#f97a13', '#f97f12', '#f88512', '#f88a11', '#f88f11', '#f79510',
              '#f79a10', '#f79f0f', '#f6a50f', '#f6aa0e', '#f6af0e', '#f5b50d',
              '#f5ba0d', '#f5bf0c', '#f4c50c', '#f4ca0b', '#f4cf0b', '#f4d40a',
              '#f3da0a', '#f3df09', '#f3e409', '#f2ea08', '#f2ef08', '#f2f407',
              '#f1fa07', '#f1ff06']
keda_list = ['#fefbf4', '#fdf5e5', '#fbf2d9', '#f9edcc', '#f8eac0', '#f7e8b6',
             '#f7e4ab', '#f6e0a1', '#f5de97', '#f4da8d', '#f2d785', '#f1d37c',
             '#f1d172', '#f0ce6b', '#f1cb63', '#efc85d', '#efc653', '#eec24c',
             '#eebf47', '#e9ba46', '#e8b546', '#e4b046', '#e2ab46', '#dea545',
             '#dca244', '#d99c44', '#d79845', '#d49344', '#d28d42', '#cf8a43',
             '#cd8643', '#cb8243', '#c87b42', '#c57740', '#c2723f', '#c16e3f',
             '#bd693f', '#b76841', '#b06843', '#a96845', '#a2674a', '#9b664c',
             '#94664e', '#8e6652', '#876655', '#816558', '#7a655b', '#75655f',
             '#6f6561', '#696465', '#636468', '#5e646c', '#59636f', '#536272',
             '#4f6175', '#4b6078', '#495e78', '#475a77', '#465877', '#455475',
             '#435174', '#424f73', '#404b72', '#3f4971', '#3e4670', '#3c4470',
             '#3b406e', '#393e6d', '#383c6c', '#36386b', '#353769', '#343469',
             '#323369', '#313066', '#302d63', '#2e2c5d', '#2c2a55', '#2a284f',
             '#272549', '#252445', '#23213f', '#211e39', '#1f1c33', '#1c1a2e',
             '#1a1829', '#181724', '#161521', '#15141d', '#141319', '#121216',
             '#111113']

young = mpl_c.LinearSegmentedColormap.from_list('young', young_list)
young_r = mpl_c.LinearSegmentedColormap.from_list('young_r', young_list[::-1])
BluePurpleRedor = mpl_c.LinearSegmentedColormap.from_list('BluePurpleRedor', BluePurpleRedor_list)
BluePurpleRedor_r = mpl_c.LinearSegmentedColormap.from_list('BluePurpleRedor_r', BluePurpleRedor_list[::-1])
PrinsensvlagLinear = mpl_c.LinearSegmentedColormap.from_list('PrinsensvlagLinear', PrinsensvlagLinear_list)
PrinsensvlagLinear_r = mpl_c.LinearSegmentedColormap.from_list('PrinsensvlagLinear_r', PrinsensvlagLinear_list[::-1])
nihit = mpl_c.LinearSegmentedColormap.from_list('nihit', nihit_list)
nihit_r = mpl_c.LinearSegmentedColormap.from_list('nihit_r', nihit_list[::-1])
keda = mpl_c.LinearSegmentedColormap.from_list('keda', keda_list)
keda_r = mpl_c.LinearSegmentedColormap.from_list('keda_r', keda_list[::-1])

def invert_lightness( colors ):
    shape = colors.shape
    C = colors.reshape((-1,shape[-1]))
    R = np.copy(C[:,0])
    G = np.copy(C[:,1])
    B = np.copy(C[:,2])
    A = np.copy(C[:,3])
    final = [1.-0.5*(G+B), 1.-0.5*(R+B), 1.-0.5*(R+G), A]
    return np.array(final).T.reshape(shape)

def stretch_center( cmap, fac, use_hyper=False, inv_l=False, endpoint=1.0 ):
    funs = (np.arctan, np.tan)
    if use_hyper:
        funs = (np.tanh, np.arctanh)
    xm = funs[0](fac)
    ary = (funs[1]( np.linspace(-xm*endpoint, xm*endpoint, 1024) ) + fac)/(2*fac)
    colors = cmap(ary)
    if inv_l:
        colors = invert_lightness(colors)
    return mpl_c.LinearSegmentedColormap.from_list( 'CmapCustom', colors )

if __name__ == '__main__':
    import matplotlib.pyplot as plt
    import scipy.special as scs
    im = np.linspace(0,1,100)[None,:]
    plt.imshow( im, aspect='auto', cmap=wdiv2 )

    for map in [bdiv0, bdiv1, bdiv2]:
        x = np.linspace(-1,1,256)
        x, y = np.meshgrid(x,x)

        r = x**2+y**2

        z = scs.jv(3, 30*np.sqrt(r))
        fig = plt.figure( figsize=(9,9) )
        ax = fig.add_axes( [0,0,1,1] )
        ax.imshow(z, cmap=map, aspect='auto', interpolation='bicubic')
        ax.text( 0.5, 0.99, map.name, transform=ax.transAxes, ha='center', va='top', c='white' )
        ax.set_axis_off()

    # fig.savefig('image.jpg', dpi=400)
    plt.show()

