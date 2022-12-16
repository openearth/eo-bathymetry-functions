sdb_job_configs = {
  sdb_nl = {
      description = "Job to generate the SDB of the area around Den Helder, NL",
      cron_schedule = "0 1 1 */3 *",  # 01:00 every 3rd month (March / June / September / December)
      time_zone = "Europe/Amsterdam",
      http_method = "POST",
      uri = "https://europe-west1-bathymetry.cloudfunctions.net/export-tile-bathymetry",
      coordinates = [
        [
          2.1379114173288514,
          51.293128274491586
        ],
        [
          2.434577524665388,
          50.920604754698104
        ],
        [
          3.4893648519040497,
          51.279391915875294
        ],
        [
          4.390334104842521,
          51.23813955644665
        ],
        [
          4.588103498320728,
          51.791975126338585
        ],
        [
          4.247490876553768,
          51.988625950681566
        ],
        [
          4.577112318328558,
          52.26518569517875
        ],
        [
          5.708821537267085,
          52.21136023592507
        ],
        [
          6.071406826426948,
          52.64015877655301
        ],
        [
          5.554993523607437,
          53.011941826417356
        ],
        [
          5.664867560921258,
          53.242693789891696
        ],
        [
          6.455968041721454,
          53.308396205716384
        ],
        [
          6.96139337053084,
          53.150542436017325
        ],
        [
          7.433856177115076,
          53.20322469622837
        ],
        [
          7.258056716197917,
          53.49836041191256
        ],
        [
          7.807433270201252,
          53.64190547111388
        ],
        [
          7.851382131427519,
          53.36744056524093
        ],
        [
          8.246932075595723,
          53.28212603987968
        ],
        [
          8.49964597768004,
          53.45258254510429
        ],
        [
          8.664460539456957,
          53.68747514808856
        ],
        [
          9.224824499059359,
          53.70048477855259
        ],
        [
          9.433589198160542,
          53.85630714886521
        ],
        [
          9.005076898848566,
          54.01800983912456
        ],
        [
          9.027054533151027,
          54.288259107842684
        ],
        [
          8.928170962953667,
          54.76647039361107
        ],
        [
          8.730397048304514,
          55.050715099021765
        ],
        [
          8.609537217180126,
          55.495118852064124
        ],
        [
          8.499663415186113,
          55.78657274380671
        ],
        [
          8.444935713313976,
          56.13358302289527
        ],
        [
          7.790672344250559,
          56.114654415229566
        ],
        [
          7.801747861258406,
          54.44588196627105
        ],
        [
          8.042203318168877,
          53.944119456233665
        ],
        [
          4.594031111232071,
          53.51319216872026
        ],
        [
          3.8075274264251737,
          52.25509342522693
        ],
        [
          3.304397467015563,
          51.531693064795505
        ]
      ]
      zoom = 9,
      export_zoom = 13,
      step_months = 3,
      window_years = 2,
      asset_path = "projects/deltares-rws/eo-bathymetry/subtidal-nl"
  }
}

# sdb_job_configs = {
#     sdb_t1 = {
#         description = "Job to generate the SDB at the European east coast.",
#         cron_schedule = "0 1 1 */3 *",  # 01:00 every 3rd month (March / June / September / December)
#         time_zone = "Europe/Amsterdam",
#         http_method = "POST",
#         uri = "https://europe-west1-bathymetry.cloudfunctions.net/export-tile-bathymetry",
#         coordinates = [
#             [
#                 0.0,
#                 50.736455
#             ],
#             [
#                 2.8125,
#                 50.736455
#             ],
#             [
#                 2.8125,
#                 52.48278
#             ],
#             [
#                 0.0,
#                 52.48278
#             ],
#             [
#                 0.0,
#                 50.736455
#             ]
#         ]
#         zoom = 9,
#         export_zoom = 13,
#         step_months = 3,
#         window_years = 2,
#         asset_path = "projects/deltares-rws/eo-bathymetry/depth-uncalibrated"
#     },
#     sdb_t2 = {
#         description = "Job to generate the SDB at the European east coast.",
#         cron_schedule = "0 1 1 */3 *",  # 01:00 every 3rd month (March / June / September / December)
#         time_zone = "Europe/Amsterdam",
#         http_method = "POST",
#         uri = "https://europe-west1-bathymetry.cloudfunctions.net/export-tile-bathymetry",
#         coordinates = [
#             [
#                 2.8125,
#                 52.48278
#             ],
#             [
#                 5.625,
#                 52.48278
#             ],
#             [
#                 5.625,
#                 54.162434
#             ],
#             [
#                 2.8125,
#                 54.162434
#             ],
#             [
#                 2.8125,
#                 52.48278
#             ]
#         ]
#         zoom = 9,
#         export_zoom = 13,
#         step_months = 3,
#         window_years = 2,
#         asset_path = "projects/deltares-rws/eo-bathymetry/depth-uncalibrated"
#     },
#     sdb_t3 = {
#         description = "Job to generate the SDB at the European east coast.",
#         cron_schedule = "0 1 1 */3 *",  # 01:00 every 3rd month (March / June / September / December)
#         time_zone = "Europe/Amsterdam",
#         http_method = "POST",
#         uri = "https://europe-west1-bathymetry.cloudfunctions.net/export-tile-bathymetry",
#         coordinates = [
#             [
#                 2.8125,
#                 50.736455
#             ],
#             [
#                 5.625,
#                 50.736455
#             ],
#             [
#                 5.625,
#                 52.48278
#             ],
#             [
#                 2.8125,
#                 52.48278
#             ],
#             [
#                 2.8125,
#                 50.736455
#             ]
#         ]
#         zoom = 9,
#         export_zoom = 13,
#         step_months = 3,
#         window_years = 2,
#         asset_path = "projects/deltares-rws/eo-bathymetry/depth-uncalibrated"
#     },
#     sdb_t4 = {
#         description = "Job to generate the SDB at the European east coast.",
#         cron_schedule = "0 1 1 */3 *",  # 01:00 every 3rd month (March / June / September / December)
#         time_zone = "Europe/Amsterdam",
#         http_method = "POST",
#         uri = "https://europe-west1-bathymetry.cloudfunctions.net/export-tile-bathymetry",
#         coordinates = [
#             [
#                 5.625,
#                 55.776573
#             ],
#             [
#                 8.4375,
#                 55.776573
#             ],
#             [
#                 8.4375,
#                 57.326521
#             ],
#             [
#                 5.625,
#                 57.326521
#             ],
#             [
#                 5.625,
#                 55.776573
#             ]
#         ]
#         zoom = 9,
#         export_zoom = 13,
#         step_months = 3,
#         window_years = 2,
#         asset_path = "projects/deltares-rws/eo-bathymetry/depth-uncalibrated"
#     },
#     sdb_t5 = {
#         description = "Job to generate the SDB at the European east coast.",
#         cron_schedule = "0 1 1 */3 *",  # 01:00 every 3rd month (March / June / September / December)
#         time_zone = "Europe/Amsterdam",
#         http_method = "POST",
#         uri = "https://europe-west1-bathymetry.cloudfunctions.net/export-tile-bathymetry",
#         coordinates = [
#         [
#             5.625,
#             54.162434
#         ],
#         [
#             8.4375,
#             54.162434
#         ],
#         [
#             8.4375,
#             55.776573
#         ],
#         [
#             5.625,
#             55.776573
#         ],
#         [
#             5.625,
#             54.162434
#         ]
#         ]
#         zoom = 9,
#         export_zoom = 13,
#         step_months = 3,
#         window_years = 2,
#         asset_path = "projects/deltares-rws/eo-bathymetry/depth-uncalibrated"
#     },
#     sdb_t6 = {
#         description = "Job to generate the SDB at the European east coast.",
#         cron_schedule = "0 1 1 */3 *",  # 01:00 every 3rd month (March / June / September / December)
#         time_zone = "Europe/Amsterdam",
#         http_method = "POST",
#         uri = "https://europe-west1-bathymetry.cloudfunctions.net/export-tile-bathymetry",
#         coordinates = [
#             [
#                 5.625,
#                 52.48278
#             ],
#             [
#                 8.4375,
#                 52.48278
#             ],
#             [
#                 8.4375,
#                 54.162434
#             ],
#             [
#                 5.625,
#                 54.162434
#             ],
#             [
#                 5.625,
#                 52.48278
#             ]
#         ]
#         zoom = 9,
#         export_zoom = 13,
#         step_months = 3,
#         window_years = 2,
#         asset_path = "projects/deltares-rws/eo-bathymetry/depth-uncalibrated"
#     },
#     sdb_t7 = {
#         description = "Job to generate the SDB at the European east coast.",
#         cron_schedule = "0 1 1 */3 *",  # 01:00 every 3rd month (March / June / September / December)
#         time_zone = "Europe/Amsterdam",
#         http_method = "POST",
#         uri = "https://europe-west1-bathymetry.cloudfunctions.net/export-tile-bathymetry",
#         coordinates = [
#             [
#                 5.625,
#                 50.736455
#             ],
#             [
#                 8.4375,
#                 50.736455
#             ],
#             [
#                 8.4375,
#                 52.48278
#             ],
#             [
#                 5.625,
#                 52.48278
#             ],
#             [
#                 5.625,
#                 50.736455
#             ]
#         ]
#         zoom = 9,
#         export_zoom = 13,
#         step_months = 3,
#         window_years = 2,
#         asset_path = "projects/deltares-rws/eo-bathymetry/depth-uncalibrated"
#     },
#     sdb_t8 = {
#         description = "Job to generate the SDB at the European east coast.",
#         cron_schedule = "0 1 1 */3 *",  # 01:00 every 3rd month (March / June / September / December)
#         time_zone = "Europe/Amsterdam",
#         http_method = "POST",
#         uri = "https://europe-west1-bathymetry.cloudfunctions.net/export-tile-bathymetry",
#         coordinates = [
#             [
#                 8.4375,
#                 55.776573
#             ],
#             [
#                 11.25,
#                 55.776573
#             ],
#             [
#                 11.25,
#                 57.326521
#             ],
#             [
#                 8.4375,
#                 57.326521
#             ],
#             [
#                 8.4375,
#                 55.776573
#             ]
#         ]
#         zoom = 9,
#         export_zoom = 13,
#         step_months = 3,
#         window_years = 2,
#         asset_path = "projects/deltares-rws/eo-bathymetry/depth-uncalibrated"
#     },
#     sdb_t9 = {
#         description = "Job to generate the SDB at the European east coast.",
#         cron_schedule = "0 1 1 */3 *",  # 01:00 every 3rd month (March / June / September / December)
#         time_zone = "Europe/Amsterdam",
#         http_method = "POST",
#         uri = "https://europe-west1-bathymetry.cloudfunctions.net/export-tile-bathymetry",
#         coordinates = [
#             [
#                 8.4375,
#                 52.48278
#             ],
#             [
#                 11.25,
#                 52.48278
#             ],
#             [
#                 11.25,
#                 54.162434
#             ],
#             [
#                 8.4375,
#                 54.162434
#             ],
#             [
#                 8.4375,
#                 52.48278
#             ]
#         ]
#         zoom = 9,
#         export_zoom = 13,
#         step_months = 3,
#         window_years = 2,
#         asset_path = "projects/deltares-rws/eo-bathymetry/depth-uncalibrated"
#     },
#     sdb_t10 = {
#         description = "Job to generate the SDB at the European east coast.",
#         cron_schedule = "0 1 1 */3 *",  # 01:00 every 3rd month (March / June / September / December)
#         time_zone = "Europe/Amsterdam",
#         http_method = "POST",
#         uri = "https://europe-west1-bathymetry.cloudfunctions.net/export-tile-bathymetry",
#         coordinates = [
#             [
#                 2.8125,
#                 50.736455
#             ],
#             [
#                 5.625,
#                 50.736455
#             ],
#             [
#                 5.625,
#                 52.48278
#             ],
#             [
#                 2.8125,
#                 52.48278
#             ],
#             [
#                 2.8125,
#                 50.736455
#             ]
#         ]
#         zoom = 9,
#         export_zoom = 13,
#         step_months = 3,
#         window_years = 2,
#         asset_path = "projects/deltares-rws/eo-bathymetry/depth-uncalibrated"
#     }
# }


rgb_job_configs = {
  rgb_nl = {
      # coordinates = [
      #     [
      #         5.795880648281493,
      #         51.52322043928555
      #     ],
      #     [
      #         7.597638460781493,
      #         52.60383266102908
      #     ],
      #     [
      #         10.014630648281493,
      #         53.38409943602731
      #     ],
      #     [
      #         10.168439242031493,
      #         54.26597908534566
      #     ],
      #     [
      #         9.245587679531493,
      #         56.0604912541101
      #     ],
      #     [
      #         7.092267367031493,
      #         56.207423002919064
      #     ],
      #     [
      #         7.158185335781493,
      #         55.09168342821415
      #     ],
      #     [
      #         6.608868929531493,
      #         54.59827676009737
      #     ],
      #     [
      #         3.928204867031493,
      #         54.16319085617696
      #     ],
      #     [
      #         2.368146273281493,
      #         52.25550015782851
      #     ],
      #     [
      #         2.434064242031493,
      #         51.16637724261702
      #     ],
      #     [
      #         3.642560335781493,
      #         50.80675167573701
      #     ],
      #     [
      #         5.795880648281493,
      #         51.52322043928555
      #     ]
      # ],
      coordinates = [
        [
          2.1379114173288514,
          51.293128274491586
        ],
        [
          2.434577524665388,
          50.920604754698104
        ],
        [
          3.4893648519040497,
          51.279391915875294
        ],
        [
          4.390334104842521,
          51.23813955644665
        ],
        [
          4.588103498320728,
          51.791975126338585
        ],
        [
          4.247490876553768,
          51.988625950681566
        ],
        [
          4.577112318328558,
          52.26518569517875
        ],
        [
          5.708821537267085,
          52.21136023592507
        ],
        [
          6.071406826426948,
          52.64015877655301
        ],
        [
          5.554993523607437,
          53.011941826417356
        ],
        [
          5.664867560921258,
          53.242693789891696
        ],
        [
          6.455968041721454,
          53.308396205716384
        ],
        [
          6.96139337053084,
          53.150542436017325
        ],
        [
          7.433856177115076,
          53.20322469622837
        ],
        [
          7.258056716197917,
          53.49836041191256
        ],
        [
          7.807433270201252,
          53.64190547111388
        ],
        [
          7.851382131427519,
          53.36744056524093
        ],
        [
          8.246932075595723,
          53.28212603987968
        ],
        [
          8.49964597768004,
          53.45258254510429
        ],
        [
          8.664460539456957,
          53.68747514808856
        ],
        [
          9.224824499059359,
          53.70048477855259
        ],
        [
          9.433589198160542,
          53.85630714886521
        ],
        [
          9.005076898848566,
          54.01800983912456
        ],
        [
          9.027054533151027,
          54.288259107842684
        ],
        [
          8.928170962953667,
          54.76647039361107
        ],
        [
          8.730397048304514,
          55.050715099021765
        ],
        [
          8.609537217180126,
          55.495118852064124
        ],
        [
          8.499663415186113,
          55.78657274380671
        ],
        [
          8.444935713313976,
          56.13358302289527
        ],
        [
          7.790672344250559,
          56.114654415229566
        ],
        [
          7.801747861258406,
          54.44588196627105
        ],
        [
          8.042203318168877,
          53.944119456233665
        ],
        [
          4.594031111232071,
          53.51319216872026
        ],
        [
          3.8075274264251737,
          52.25509342522693
        ],
        [
          3.304397467015563,
          51.531693064795505
        ]
      ],
      description = "Job to generate the SDB of the area around Den Helder, NL",
      cron_schedule = "0 1 2 */3 *",  # 01:00 the 2nd day of every 3rd month (March / June / September / December)
      time_zone = "Europe/Amsterdam",
      http_method = "POST",
      uri = "https://europe-west1-bathymetry.cloudfunctions.net/generate-rgb-tiles",
      image_collection = "projects/deltares-rws/eo-bathymetry/subtidal-nl",
      min_zoom = 0,
      max_zoom = 13
  }
}
