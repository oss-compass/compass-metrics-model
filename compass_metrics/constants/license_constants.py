# 定义许可证兼容性矩阵
LICENSE_COMPATIBILITY = {
    'mit': ['mit', 'apache-2.0', 'gpl-2.0', 'gpl-3.0', 'lgpl-2.1', 'lgpl-3.0'],
    'amazon-sl': ['amazon-sl'],
    'lgpl-2.1': ['lgpl-2.1', 'lgpl-2.1-plus', 'lgpl-3.0', 'gpl-2.0', 'gpl-2.0-plus', 'gpl-3.0', 'agpl-3.0',
                 'artistic-2.0', 'eupl-1.2', 'rpsl-1.0', 'sleepycat', 'apache-2.0', 'ecl-2.0'],
    'lgpl-2.1-plus': ['lgpl-2.1', 'lgpl-2.1-plus', 'lgpl-3.0', 'gpl-2.0', 'gpl-2.0-plus', 'gpl-3.0', 'agpl-3.0',
                      'artistic-2.0', 'eupl-1.2', 'rpsl-1.0', 'sleepycat', 'apache-2.0', 'ecl-2.0'],
    'lgpl-3.0': ['lgpl-2.1', 'lgpl-2.1-plus', 'lgpl-3.0', 'gpl-2.0-plus', 'gpl-3.0', 'agpl-3.0', 'artistic-2.0',
                 'eupl-1.2', 'rpsl-1.0', 'sleepycat', 'apache-2.0', 'ecl-2.0'],
    'gpl-2.0': ['lgpl-2.1', 'lgpl-2.1-plus', 'gpl-2.0', 'gpl-2.0-plus', 'artistic-2.0', 'cecill-2.1', 'eupl-1.1',
                'eupl-1.2', 'vim', 'rpsl-1.0', 'sleepycat'],
    'gpl-2.0-plus': ['lgpl-2.1', 'lgpl-2.1-plus', 'lgpl-3.0', 'gpl-2.0', 'gpl-2.0-plus', 'gpl-3.0', 'agpl-3.0',
                     'artistic-2.0', 'cecill-2.1', 'epl-2.0', 'eupl-1.2', 'vim', 'rpsl-1.0', 'sleepycat', 'apache-2.0',
                     'ecl-2.0'],
    'gpl-3.0': ['lgpl-2.1', 'lgpl-2.1-plus', 'lgpl-3.0', 'gpl-2.0-plus', 'gpl-3.0', 'agpl-3.0', 'artistic-2.0',
                'cecill-2.1', 'epl-2.0', 'eupl-1.2', 'vim', 'rpsl-1.0', 'sleepycat', 'apache-2.0', 'ecl-2.0'],
    'agpl-3.0': ['lgpl-2.1', 'lgpl-2.1-plus', 'lgpl-3.0', 'gpl-2.0-plus', 'gpl-3.0', 'agpl-3.0', 'artistic-2.0',
                 'cecill-2.1', 'eupl-1.2', 'vim', 'rpsl-1.0', 'sleepycat', 'apache-2.0', 'ecl-2.0'],
    'artistic-2.0': ['lgpl-2.1', 'lgpl-2.1-plus', 'lgpl-3.0', 'gpl-2.0', 'gpl-2.0-plus', 'gpl-3.0', 'agpl-3.0',
                     'artistic-2.0', 'cecill-2.1', 'epl-1.0', 'epl-2.0', 'eupl-1.1', 'eupl-1.2', 'mpl-2.0', 'ms-rl',
                     'osl-3.0', 'vim', 'cddl-1.0', 'cpal-1.0', 'cpl-1.0', 'ibmpl-1.0', 'lucent-pl-1.02', 'nokos-1.0a',
                     'rpsl-1.0', 'sun-sissl-1.1', 'sleepycat', 'spl-1.0', 'php-3.01', 'apache-2.0', 'ecl-2.0'],
    'cecill-2.1': ['gpl-2.0', 'gpl-2.0-plus', 'gpl-3.0', 'agpl-3.0', 'artistic-2.0', 'cecill-2.1', 'eupl-1.1',
                   'eupl-1.2', 'lucent-pl-1.02', 'php-3.01', 'apache-2.0', 'ecl-2.0'],
    'epl-1.0': ['artistic-2.0', 'epl-1.0', 'epl-2.0', 'eupl-1.1', 'eupl-1.2', 'lucent-pl-1.02', 'sun-sissl-1.1',
                'php-3.01', 'apache-2.0', 'ecl-2.0'],
    'epl-2.0': ['gpl-2.0-plus', 'gpl-3.0', 'artistic-2.0', 'epl-1.0', 'epl-2.0', 'lucent-pl-1.02', 'sun-sissl-1.1',
                'php-3.01', 'apache-2.0', 'ecl-2.0'],
    'eupl-1.1': ['gpl-2.0', 'artistic-2.0', 'cecill-2.1', 'epl-1.0', 'eupl-1.1', 'eupl-1.2', 'osl-3.0', 'cpl-1.0',
                 'lucent-pl-1.02', 'php-3.01', 'apache-2.0', 'ecl-2.0'],
    'eupl-1.2': ['lgpl-2.1', 'lgpl-2.1-plus', 'lgpl-3.0', 'gpl-2.0', 'gpl-2.0-plus', 'gpl-3.0', 'agpl-3.0',
                 'artistic-2.0', 'cecill-2.1', 'epl-1.0', 'eupl-1.1', 'eupl-1.2', 'mpl-2.0', 'osl-3.0',
                 'lucent-pl-1.02', 'php-3.01', 'apache-2.0', 'ecl-2.0'],
    'mpl-2.0': ['lgpl-2.1', 'lgpl-2.1-plus', 'lgpl-3.0', 'gpl-2.0', 'gpl-2.0-plus', 'gpl-3.0', 'agpl-3.0',
                'artistic-2.0', 'eupl-1.2', 'mpl-2.0', 'lucent-pl-1.02', 'php-3.01', 'apache-2.0', 'ecl-2.0'],
    'ms-rl': ['artistic-2.0', 'ms-rl', 'lucent-pl-1.02', 'php-3.01', 'apache-2.0', 'ecl-2.0'],
    'osl-3.0': ['artistic-2.0', 'eupl-1.1', 'eupl-1.2', 'osl-3.0', 'lucent-pl-1.02', 'php-3.01', 'apache-2.0',
                'ecl-2.0'],
    'vim': ['lgpl-2.1', 'lgpl-2.1-plus', 'lgpl-3.0', 'gpl-2.0', 'gpl-2.0-plus', 'gpl-3.0', 'agpl-3.0', 'artistic-2.0',
            'vim', 'lucent-pl-1.02', 'php-3.01', 'apache-2.0', 'ecl-2.0'],
    'cddl-1.0': ['artistic-2.0', 'cddl-1.0', 'lucent-pl-1.02', 'php-3.01', 'apache-2.0', 'ecl-2.0'],
    'cpal-1.0': ['artistic-2.0', 'cpal-1.0', 'php-3.01', 'apache-2.0', 'ecl-2.0'],
    'cpl-1.0': ['artistic-2.0', 'eupl-1.1', 'cpl-1.0', 'php-3.01', 'apache-2.0', 'ecl-2.0'],
    'ibmpl-1.0': ['artistic-2.0', 'ibmpl-1.0', 'php-3.01', 'apache-2.0', 'ecl-2.0'],
    'lucent-pl-1.02': ['artistic-2.0', 'cecill-2.1', 'epl-1.0', 'epl-2.0', 'eupl-1.1', 'eupl-1.2', 'mpl-2.0', 'ms-rl',
                       'osl-3.0', 'vim', 'cddl-1.0', 'cpal-1.0', 'cpl-1.0', 'ibmpl-1.0', 'lucent-pl-1.02', 'nokos-1.0a',
                       'rpsl-1.0', 'sun-sissl-1.1', 'sleepycat', 'spl-1.0', 'php-3.01', 'apache-2.0', 'ecl-2.0'],
    'nokos-1.0a': ['artistic-2.0', 'nokos-1.0a', 'php-3.01', 'apache-2.0', 'ecl-2.0'],
    'rpsl-1.0': ['lgpl-2.1', 'lgpl-2.1-plus', 'lgpl-3.0', 'gpl-2.0', 'gpl-2.0-plus', 'gpl-3.0', 'agpl-3.0',
                 'artistic-2.0', 'mpl-2.0', 'cpl-1.0', 'ibmpl-1.0', 'rpsl-1.0', 'php-3.01', 'apache-2.0', 'ecl-2.0'],
    'sun-sissl-1.1': ['artistic-2.0', 'lucent-pl-1.02', 'sun-sissl-1.1', 'php-3.01', 'apache-2.0', 'ecl-2.0'],
    'sleepycat': ['lgpl-2.1', 'lgpl-2.1-plus', 'lgpl-3.0', 'gpl-2.0', 'gpl-2.0-plus', 'gpl-3.0', 'agpl-3.0',
                  'artistic-2.0', 'lucent-pl-1.02', 'sleepycat', 'php-3.01', 'apache-2.0', 'ecl-2.0'],
    'spl-1.0': ['artistic-2.0', 'lucent-pl-1.02', 'spl-1.0', 'php-3.01', 'apache-2.0', 'ecl-2.0'],
    'apache-2.0': ['lgpl-2.1', 'lgpl-2.1-plus', 'lgpl-3.0', 'gpl-2.0-plus', 'gpl-3.0', 'agpl-3.0', 'artistic-2.0',
                   'cecill-2.1', 'epl-1.0', 'epl-2.0', 'eupl-1.1', 'eupl-1.2', 'mpl-2.0', 'ms-rl', 'osl-3.0', 'vim',
                   'cddl-1.0', 'cpal-1.0', 'cpl-1.0', 'ibmpl-1.0', 'lucent-pl-1.02', 'nokos-1.0a', 'rpsl-1.0',
                   'sun-sissl-1.1', 'sleepycat', 'spl-1.0', 'php-3.01', 'apache-2.0', 'ecl-2.0'],
    'ecl-2.0': ['lgpl-2.1', 'lgpl-2.1-plus', 'lgpl-3.0', 'gpl-2.0-plus', 'gpl-3.0', 'agpl-3.0', 'artistic-2.0',
                'cecill-2.1', 'epl-1.0', 'epl-2.0', 'eupl-1.1', 'eupl-1.2', 'mpl-2.0', 'ms-rl', 'osl-3.0', 'vim',
                'cddl-1.0', 'cpal-1.0', 'cpl-1.0', 'ibmpl-1.0', 'lucent-pl-1.02', 'nokos-1.0a', 'rpsl-1.0',
                'sun-sissl-1.1', 'sleepycat', 'spl-1.0', 'php-3.01', 'apache-2.0', 'ecl-2.0'],
    'php-3.01': ['artistic-2.0', 'cecill-2.1', 'epl-1.0', 'epl-2.0', 'eupl-1.1', 'eupl-1.2', 'mpl-2.0', 'ms-rl',
                 'osl-3.0', 'vim', 'cddl-1.0', 'cpal-1.0', 'cpl-1.0', 'ibmpl-1.0', 'lucent-pl-1.02', 'nokos-1.0a',
                 'rpsl-1.0', 'sun-sissl-1.1', 'sleepycat', 'spl-1.0', 'php-3.01', 'apache-2.0', 'ecl-2.0'],
}

# 定义允许修改后闭源的许可证列表
COMMERCIAL_ALLOWED_LICENSES = [
    # 宽松许可证
    'mit',
    'bsd-2-clause',
    'bsd-3-clause',
    'bsd-4-clause',
    'apache-2.0',
    'isc',
    'ms-pl',
    'x11',
    'zlib',
    # 弱著作权许可证
    'lgpl-2.1',
    'lgpl-2.1-plus',
    'lgpl-3.0',
    'mpl-2.0',
    'cddl-1.0',
    'epl-1.0',
    'epl-2.0',
    'cpl-1.0',
    # 其他允许闭源的许可证
    'php-3.01',
    'python-2.0',
    'ruby',
    'artistic-2.0',
    'ecl-2.0',
    'osl-3.0',
    'intel'
]

# 定义宽松型和弱著作权许可证列表
WEAK_LICENSES = {
    # 宽松型许可证
    'mit',  # MIT许可证
    'apache-2.0',  # Apache 2.0
    'bsd-2-clause',  # BSD 2-Clause
    'bsd-3-clause',  # BSD 3-Clause
    'bsd-0-clause',  # BSD Zero Clause
    'isc',  # ISC许可证
    'artistic-2.0',  # Artistic License 2.0
    'python-2.0',  # Python License 2.0
    'zlib',  # zlib/libpng许可证
    'x11',  # X11许可证
    'unlicense',  # The Unlicense
    'wtfpl',  # Do What The F*ck You Want To Public License
    'cc0-1.0',  # Creative Commons Zero v1.0 Universal

    # 弱著作权许可证
    'lgpl-2.0',  # LGPL 2.0
    'lgpl-2.1',  # LGPL 2.1
    'lgpl-3.0',  # LGPL 3.0
    'mpl-1.1',  # Mozilla Public License 1.1
    'mpl-2.0',  # Mozilla Public License 2.0
    'cddl-1.0',  # Common Development and Distribution License 1.0
    'epl-1.0',  # Eclipse Public License 1.0
    'epl-2.0',  # Eclipse Public License 2.0
    'ms-pl',  # Microsoft Public License
    'osl-3.0',  # Open Software License 3.0
}

# 定义需要声明变更的许可证列表
CLAIM_REQUIRED_LICENSES = {
    # GNU系列
    'gpl-1.0',  # GPL 1.0要求声明修改
    'gpl-2.0',  # GPL 2.0要求声明修改
    'gpl-3.0',  # GPL 3.0要求声明修改
    'lgpl-2.0',  # LGPL 2.0要求声明修改
    'lgpl-2.1',  # LGPL 2.1要求声明修改
    'lgpl-3.0',  # LGPL 3.0要求声明修改
    'agpl-1.0',  # AGPL 1.0要求声明修改
    'agpl-3.0',  # AGPL 3.0要求声明修改

    # Mozilla系列
    'mpl-1.0',  # Mozilla Public License 1.0要求声明修改
    'mpl-1.1',  # Mozilla Public License 1.1要求声明修改
    'mpl-2.0',  # Mozilla Public License 2.0要求声明修改

    # 欧盟和其他国家的许可证
    'eupl-1.1',  # European Union Public License 1.1要求声明修改
    'eupl-1.2',  # European Union Public License 1.2要求声明修改
    'cecill-2.1',  # CeCILL Free Software License Agreement要求声明修改

    # 其他要求声明的许可证
    'apache-2.0',  # Apache 2.0要求声明修改
    'ms-rl',  # Microsoft Reciprocal License要求声明修改
    'osl-3.0',  # Open Software License 3.0要求声明修改
    'artistic-2.0',  # Artistic License 2.0要求声明修改
    'epl-1.0',  # Eclipse Public License 1.0要求声明修改
    'epl-2.0',  # Eclipse Public License 2.0要求声明修改
    'cddl-1.0',  # Common Development and Distribution License 1.0要求声明修改
    'amazon-sl',  # Amazon Service License 要求声明修改
}
