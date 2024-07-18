

# 配置文件模板，使用时复制到config/actual文件夹下
accounts = {
    'account1': {
        'account_description': '油管爬取视频',  # 账号描述
        'account_tags': 'pov',
        # 账号标签
        'benchmark_accounts': [  # 对标账号列表
            {
                'platform': "youtube_shors",  # 0 Tiktok、1 抖音、2 小红书、3 B站、4 快手
                'benchmark_account_name': 'skyyjade',  # 对标账号名称
                'benchmark_account_id': '@skyyjade',
                'type': 1,  # 类型：0 普通、1 连续，默认0
                'process_strategy': "1111",
                'bgm_type': "common",
                # 对标账号ID
                'priority': 1,  # 对标账号优先级
                "video_max_time": 120,  # 视频最大时间 单位:秒
                "video_min_time": 7,  # 视频最小时间 单位:秒
                "video_num": 6  # 获取视频数量 单位:秒
            },
            {
                'platform': "youtube_shors",  # 0 Tiktok、1 抖音、2 小红书、3 B站、4 快手
                'benchmark_account_name': 'AmpWorld.',  # 对标账号名称
                'benchmark_account_id': '@AmpWorld.',
                'type': 1,  # 类型：0 普通、1 连续，默认0
                'process_strategy': "test1",
                'bgm_type': "common",
                # 对标账号ID
                'priority': 1,  # 对标账号优先级
                "video_max_time": 120,  # 视频最大时间 单位:秒
                "video_min_time": 7,  # 视频最小时间 单位:秒
                "video_num": 6  # 获取视频数量 单位:秒
            },
            {
                'platform': "youtube_shors",  # 0 Tiktok、1 抖音、2 小红书、3 B站、4 快手
                'benchmark_account_name': 'ValerieLepelch',  # 对标账号名称
                'benchmark_account_id': '@ValerieLepelch',
                'type': 1,  # 类型：0 普通、1 连续，默认0
                'process_strategy': "test1",
                'bgm_type': "common",
                # 对标账号ID
                'priority': 1,  # 对标账号优先级
                "video_max_time": 120,  # 视频最大时间 单位:秒
                "video_min_time": 7,  # 视频最小时间 单位:秒
                "video_num": 6  # 获取视频数量 单位:秒
            },
            {
                'platform': "youtube_shors",  # 0 Tiktok、1 抖音、2 小红书、3 B站、4 快手
                'benchmark_account_name': 'ElianaGhen',  # 对标账号名称
                'benchmark_account_id': '@ElianaGhen',
                'type': 1,  # 类型：0 普通、1 连续，默认0
                'process_strategy': "test1",
                'bgm_type': "common",
                # 对标账号ID
                'priority': 1,  # 对标账号优先级
                "video_max_time": 120,  # 视频最大时间 单位:秒
                "video_min_time": 7,  # 视频最小时间 单位:秒
                "video_num": 6  # 获取视频数量 单位:秒
            },
            {
                'platform': "youtube_shors",  # 0 Tiktok、1 抖音、2 小红书、3 B站、4 快手
                'benchmark_account_name': 'NoahJayWood1',  # 对标账号名称
                'benchmark_account_id': '@NoahJayWood1',
                'type': 1,  # 类型：0 普通、1 连续，默认0
                'process_strategy': "test1",
                'bgm_type': "common",
                # 对标账号ID
                'priority': 1,  # 对标账号优先级
                "video_max_time": 120,  # 视频最大时间 单位:秒
                "video_min_time": 7,  # 视频最小时间 单位:秒
                "video_num": 6  # 获取视频数量 单位:秒
            },
            {
                'platform': "youtube_shors",  # 0 Tiktok、1 抖音、2 小红书、3 B站、4 快手
                'benchmark_account_name': 'TheManniiShow',  # 对标账号名称
                'benchmark_account_id': '@TheManniiShow',
                'type': 1,  # 类型：0 普通、1 连续，默认0
                'process_strategy': "test1",
                'bgm_type': "common",
                # 对标账号ID
                'priority': 1,  # 对标账号优先级
                "video_max_time": 120,  # 视频最大时间 单位:秒
                "video_min_time": 7,  # 视频最小时间 单位:秒
                "video_num": 6  # 获取视频数量 单位:秒
            },
            {
                'platform': "youtube_shors",  # 0 Tiktok、1 抖音、2 小红书、3 B站、4 快手
                'benchmark_account_name': 'yana.chirkina',  # 对标账号名称
                'benchmark_account_id': '@yana.chirkina',
                'type': 1,  # 类型：0 普通、1 连续，默认0
                'process_strategy': "test1",
                'bgm_type': "common",
                # 对标账号ID
                'priority': 1,  # 对标账号优先级
                "video_max_time": 120,  # 视频最大时间 单位:秒
                "video_min_time": 7,  # 视频最小时间 单位:秒
                "video_num": 6  # 获取视频数量 单位:秒
            },
            {
                'platform': "youtube_shors",  # 0 Tiktok、1 抖音、2 小红书、3 B站、4 快手
                'benchmark_account_name': 'krysandkareem',  # 对标账号名称
                'benchmark_account_id': '@krysandkareem',
                'type': 1,  # 类型：0 普通、1 连续，默认0
                'process_strategy': "center",
                'bgm_type': "common",
                # 对标账号ID
                'priority': 1,  # 对标账号优先级
                "video_max_time": 120,  # 视频最大时间 单位:秒
                "video_min_time": 7,  # 视频最小时间 单位:秒
                "video_num": 6  # 获取视频数量 单位:秒
            },
            {
                'platform': "youtube_shors",  # 0 Tiktok、1 抖音、2 小红书、3 B站、4 快手
                'benchmark_account_name': 'povswithnolan',  # 对标账号名称
                'benchmark_account_id': '@povswithnolan',
                'type': 1,  # 类型：0 普通、1 连续，默认0
                'process_strategy': "center",
                'bgm_type': "common",
                # 对标账号ID
                'priority': 1,  # 对标账号优先级
                "video_max_time": 120,  # 视频最大时间 单位:秒
                "video_min_time": 7,  # 视频最小时间 单位:秒
                "video_num": 6  # 获取视频数量 单位:秒
            }, {
                'platform': "youtube_shors",  # 0 Tiktok、1 抖音、2 小红书、3 B站、4 快手
                'benchmark_account_name': 'mr.spicygremlin',  # 对标账号名称
                'benchmark_account_id': '@mr.spicygremlin',
                'type': 1,  # 类型：0 普通、1 连续，默认0
                'process_strategy': "center",
                'bgm_type': "common",
                # 对标账号ID
                'priority': 1,  # 对标账号优先级
                "video_max_time": 120,  # 视频最大时间 单位:秒
                "video_min_time": 7,  # 视频最小时间 单位:秒
                "video_num": 6  # 获取视频数量 单位:秒
            }, {
                'platform': "youtube_shors",  # 0 Tiktok、1 抖音、2 小红书、3 B站、4 快手
                'benchmark_account_name': 'brookemonk',  # 对标账号名称
                'benchmark_account_id': 'brookemonk',
                'type': 1,  # 类型：0 普通、1 连续，默认0
                'process_strategy': "center",
                'bgm_type': "common",
                # 对标账号ID
                'priority': 1,  # 对标账号优先级
                "video_max_time": 120,  # 视频最大时间 单位:秒
                "video_min_time": 7,  # 视频最小时间 单位:秒
                "video_num": 6  # 获取视频数量 单位:秒
            }
        ]

    },
    'account2': {
        'account_description': 'tiktok爬取视频',  # 账号描述
        'account_tags': 'pov',
        # 账号标签
        'benchmark_accounts': [  # 对标账号列表
            {
                'platform': "tiktook",  # 0 Tiktok、1 抖音、2 小红书、3 B站、4 快手
                'benchmark_account_name': 'pwsjfjvu',  # 对标账号名称
                'benchmark_account_id': '@pwsjfjvu',
                'type': 1,  # 类型：0 普通、1 连续，默认0
                'process_strategy': "ttest333",
                'bgm_type': "common",
                # 对标账号ID
                'priority': 1,  # 对标账号优先级
                "video_max_time": 120,  # 视频最大时间 单位:秒
                "video_min_time": 7,  # 视频最小时间 单位:秒
                "video_num": 6  # 获取视频数量 单位:秒
            },
            {
                'platform': "tiktook",  # 0 Tiktok、1 抖音、2 小红书、3 B站、4 快手
                'benchmark_account_name': 'rlvpfdg.',  # 对标账号名称
                'benchmark_account_id': '@rlvpfdg.',
                'type': 1,  # 类型：0 普通、1 连续，默认0
                'process_strategy': "ttest333",
                'bgm_type': "common",
                # 对标账号ID
                'priority': 1,  # 对标账号优先级
                "video_max_time": 120,  # 视频最大时间 单位:秒
                "video_min_time": 7,  # 视频最小时间 单位:秒
                "video_num": 6  # 获取视频数量 单位:秒
            },
            {
                'platform': "tiktook",  # 0 Tiktok、1 抖音、2 小红书、3 B站、4 快手
                'benchmark_account_name': '66yga04',  # 对标账号名称
                'benchmark_account_id': '@66yga04',
                'type': 1,  # 类型：0 普通、1 连续，默认0
                'process_strategy': "ttest333",
                'bgm_type': "common",
                # 对标账号ID
                'priority': 1,  # 对标账号优先级
                "video_max_time": 120,  # 视频最大时间 单位:秒
                "video_min_time": 7,  # 视频最小时间 单位:秒
                "video_num": 6  # 获取视频数量 单位:秒
            },
            {
                'platform': "tiktook",  # 0 Tiktok、1 抖音、2 小红书、3 B站、4 快手
                'benchmark_account_name': 'fpov8',  # 对标账号名称
                'benchmark_account_id': '@fpov8',
                'type': 1,  # 类型：0 普通、1 连续，默认0
                'process_strategy': "ttest333",
                'bgm_type': "common",
                # 对标账号ID
                'priority': 1,  # 对标账号优先级
                "video_max_time": 120,  # 视频最大时间 单位:秒
                "video_min_time": 7,  # 视频最小时间 单位:秒
                "video_num": 6  # 获取视频数量 单位:秒
            },
            {
                'platform': "tiktook",  # 0 Tiktok、1 抖音、2 小红书、3 B站、4 快手
                'benchmark_account_name': 'rydxbtme3y0nu2',  # 对标账号名称
                'benchmark_account_id': '@rydxbtme3y0nu2',
                'type': 1,  # 类型：0 普通、1 连续，默认0
                'process_strategy': "ttest333",
                'bgm_type': "common",
                # 对标账号ID
                'priority': 1,  # 对标账号优先级
                "video_max_time": 120,  # 视频最大时间 单位:秒
                "video_min_time": 7,  # 视频最小时间 单位:秒
                "video_num": 6  # 获取视频数量 单位:秒
            }
        ]

    }
}
