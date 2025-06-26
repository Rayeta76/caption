# Proyecto: Caption

## Estructura de Carpetas y Archivos

```text
├── .git/
│   ├── COMMIT_EDITMSG
│   ├── FETCH_HEAD
│   ├── HEAD
│   ├── config
│   ├── description
│   ├── hooks/
│   │   ├── applypatch-msg.sample
│   │   ├── commit-msg.sample
│   │   ├── fsmonitor-watchman.sample
│   │   ├── post-checkout
│   │   ├── post-commit
│   │   ├── post-merge
│   │   ├── post-update.sample
│   │   ├── pre-applypatch.sample
│   │   ├── pre-commit.sample
│   │   ├── pre-merge-commit.sample
│   │   ├── pre-push
│   │   ├── pre-push.sample
│   │   ├── pre-rebase.sample
│   │   ├── pre-receive.sample
│   │   ├── prepare-commit-msg.sample
│   │   ├── push-to-checkout.sample
│   │   ├── sendemail-validate.sample
│   │   └── update.sample
│   ├── index
│   ├── info/
│   │   └── exclude
│   ├── lfs/
│   │   └── tmp/
│   ├── logs/
│   │   ├── HEAD
│   │   └── refs/
│   │   │   └── heads/
│   │   │   │   └── main
│   ├── objects/
│   │   ├── 08/
│   │   │   └── 851d7f77afa7147939cd9358009dd14debadde
│   │   ├── 0f/
│   │   │   └── 5680b70ba7ad69afaf0a7567d838e7eba61ce2
│   │   ├── 11/
│   │   │   └── 3fc1e5673932d039fa2cd40b1ae6e783fcc717
│   │   ├── 12/
│   │   │   └── 283e40957107518ce1f580c0bc5aa1fb24e4d0
│   │   ├── 14/
│   │   │   └── 33f4749bd634b6cf34cedbc52d1b74ad00a2af
│   │   ├── 1d/
│   │   │   └── 38d3f8ab846d78aeabb27c9d438096d947e07e
│   │   ├── 27/
│   │   │   └── e4bbbb1686bf986780150075cf47aeffee5a63
│   │   ├── 35/
│   │   │   └── 431ab28bdd44a885147bc0cf88076d0b049eec
│   │   ├── 3a/
│   │   │   └── 308856d9d4ba8aea9d7f2f6d3ec56edf3974e0
│   │   ├── 3f/
│   │   │   └── ac97edd59059b839ca0deb847921e22e23389d
│   │   ├── 45/
│   │   │   └── e2816792ad074f8c7280456fb63f3c0ad3d845
│   │   ├── 4d/
│   │   │   └── 04476c5bb89ac1964c59f9f8d228b3fb3acffd
│   │   ├── 55/
│   │   │   └── 92427c8a16f10810a8ade48f6d8c480fa21a4c
│   │   ├── 77/
│   │   │   └── 43628796e0b7f0197cee826e39cb6d2c40e852
│   │   ├── 7d/
│   │   │   └── 148be72b9661142fe57302020fa0e62ba6c721
│   │   ├── 84/
│   │   │   └── a2d1ed1bb926e551739347b57c28c7fa8cc9ee
│   │   ├── 89/
│   │   │   └── fd3028c331a36521f69c55d89b833a21ca4473
│   │   ├── 9c/
│   │   │   └── 4dd51652238c35bbd9a6c4a1d937fd871abc57
│   │   ├── 9d/
│   │   │   ├── 0d153ce7a4765b94b5712d8718b8078207e86c
│   │   │   └── 1dcfdaf1a6857c5f83dc27019c7600e1ffaff8
│   │   ├── a4/
│   │   │   └── c08b8e7bae01da262063228d6d66eed1c74c7a
│   │   ├── a8/
│   │   │   └── 4ace78d7c7320376726f440b76afc11232e6f8
│   │   ├── ac/
│   │   │   └── 877288253fe3c293ee73f6c22da45d5f99bb0d
│   │   ├── b0/
│   │   │   └── 8ca66203caee081df9e78a9517f87e14920a41
│   │   ├── b1/
│   │   │   └── 9d078bed2f1a630cbdd2ac835d9816d49500b3
│   │   ├── cd/
│   │   │   └── c4e589aff4ee50eb357bac8a6438455024049b
│   │   ├── d5/
│   │   │   └── e2a40410aea5e35995f0f8db135c8e269585eb
│   │   ├── e6/
│   │   │   └── 9de29bb2d1d6434b8b29ae775ad8c2e48c5391
│   │   ├── eb/
│   │   │   └── 060eac7e47b8061b7d1dd4e5329713b3ab773d
│   │   ├── f4/
│   │   │   └── 1e752c42c37755a3da0134e48eaa50f3dd7c12
│   │   ├── fc/
│   │   │   └── 1da8e0438117df4bb27b053ea0b9d9c0ac9ea6
│   │   ├── fd/
│   │   │   └── acd1ac8bc80c67a2257f893f89db2be04bb199
│   │   ├── info/
│   │   └── pack/
│   └── refs/
│   │   ├── heads/
│   │   │   └── main
│   │   └── tags/
├── .gitignore
├── .vscode/
│   └── settings.json
├── README.md
├── config/
│   └── settings.yaml
├── config_safetensors.py
├── emergency-fix-script.py
├── generar_readme.py
├── main.py
├── models/
│   ├── Florence-2-large-ft-safetensors/
│   │   ├── .git/
│   │   │   ├── FETCH_HEAD
│   │   │   ├── HEAD
│   │   │   ├── config
│   │   │   ├── description
│   │   │   ├── hooks/
│   │   │   │   ├── applypatch-msg.sample
│   │   │   │   ├── commit-msg.sample
│   │   │   │   ├── fsmonitor-watchman.sample
│   │   │   │   ├── post-checkout
│   │   │   │   ├── post-commit
│   │   │   │   ├── post-merge
│   │   │   │   ├── post-update.sample
│   │   │   │   ├── pre-applypatch.sample
│   │   │   │   ├── pre-commit.sample
│   │   │   │   ├── pre-merge-commit.sample
│   │   │   │   ├── pre-push
│   │   │   │   ├── pre-push.sample
│   │   │   │   ├── pre-rebase.sample
│   │   │   │   ├── pre-receive.sample
│   │   │   │   ├── prepare-commit-msg.sample
│   │   │   │   ├── push-to-checkout.sample
│   │   │   │   ├── sendemail-validate.sample
│   │   │   │   └── update.sample
│   │   │   ├── info/
│   │   │   │   └── exclude
│   │   │   ├── lfs/
│   │   │   │   ├── incomplete/
│   │   │   │   │   ├── 4188ce5a9364c358c3e28eb3e4155985867ef70bb3ae628f1f289d6a3538310a421428375
│   │   │   │   │   └── 42ccf76a0f59876721139433b4cb4ece7d6c5e18fe55bce6c409bb6d90589cee1232300160
│   │   │   │   └── objects/
│   │   │   │   │   ├── 41/
│   │   │   │   │   │   └── 88/
│   │   │   │   │   └── 42/
│   │   │   │   │   │   └── cc/
│   │   │   ├── logs/
│   │   │   │   ├── HEAD
│   │   │   │   └── refs/
│   │   │   │   │   ├── heads/
│   │   │   │   │   │   └── main
│   │   │   │   │   └── remotes/
│   │   │   │   │   │   └── origin/
│   │   │   │   │   │   │   └── HEAD
│   │   │   ├── objects/
│   │   │   │   ├── 09/
│   │   │   │   │   └── 08acaeabb9dc89df58402bfe4a72acf4ec559b
│   │   │   │   ├── 0d/
│   │   │   │   │   └── 575637e51a4afa263b4364ab30fee454440cf2
│   │   │   │   ├── 12/
│   │   │   │   │   └── 8dab7f3829a9b75296138117007b0c8bf22464
│   │   │   │   ├── 18/
│   │   │   │   │   └── d0a34da1c062db0db2e85c118202ee6898c85b
│   │   │   │   ├── 24/
│   │   │   │   │   └── 21bbdb8a6e08a4467b76670676cbacd5281b99
│   │   │   │   ├── 29/
│   │   │   │   │   └── 1d4d43733f4c15a81ff598ec1c99fd6c18f64c
│   │   │   │   ├── 30/
│   │   │   │   │   ├── 0f662887cd094fce909de5e103abe963b115ea
│   │   │   │   │   └── 1a43d581eea751717ce8a383d9339ef1073164
│   │   │   │   ├── 33/
│   │   │   │   │   └── 201c13184620a953be09987e8f4f0890a492a0
│   │   │   │   ├── 44/
│   │   │   │   │   └── 784bc58d4cb18d3549ad71e062efcf032d9ef5
│   │   │   │   ├── 4f/
│   │   │   │   │   ├── 5118ccd2b5630a62d14c957192000de1d70e2d
│   │   │   │   │   └── 8ccf2e186c79d1379725f16fd9d1c2539869a9
│   │   │   │   ├── 53/
│   │   │   │   │   └── 8110e8fd421258847d317cb62c40b9671d07a9
│   │   │   │   ├── 58/
│   │   │   │   │   └── 6d92e18b0777d65a3c4c3ebe9d55801a890787
│   │   │   │   ├── 5c/
│   │   │   │   │   └── 1b917b2b9b548b2599792d20f7e50f6de61be3
│   │   │   │   ├── 62/
│   │   │   │   │   └── 2f74997c5612ff68d0e55063714f291d159166
│   │   │   │   ├── 6d/
│   │   │   │   │   └── 8b6c7f8318328ab301ad6dab36b175f0130403
│   │   │   │   ├── 79/
│   │   │   │   │   └── c52aaead742515b7cf2d46578acfd3c2568ceb
│   │   │   │   ├── 7b/
│   │   │   │   │   └── e5fc7f47d5db027d120b8024982df93db95b74
│   │   │   │   ├── 83/
│   │   │   │   │   ├── 854a18bb0f595674561d60738144df02c21da3
│   │   │   │   │   └── 99fea35e5468e4a6023a05c7f12d04d0755727
│   │   │   │   ├── 85/
│   │   │   │   │   └── cd7be3568df661ad536b6ab20d59b08ba079ae
│   │   │   │   ├── 93/
│   │   │   │   │   └── e506126ff191af99f5bf72b18d08638634378d
│   │   │   │   ├── 94/
│   │   │   │   │   └── a2f4fd50e976bda926c700291522ea1a79323f
│   │   │   │   ├── 95/
│   │   │   │   │   └── 341e1d6ae4b5086e60f09e98f1a4ef42aca7fa
│   │   │   │   ├── 96/
│   │   │   │   │   └── 5ef0f53eca969b896f91abe8b5e74f910f1d91
│   │   │   │   ├── 98/
│   │   │   │   │   └── dbe8151818f8707fbefd935d8152f5f68e3024
│   │   │   │   ├── 9b/
│   │   │   │   │   └── 1cdec1c01073aa0b0a4bdcd5ce0989da38bf95
│   │   │   │   ├── 9e/
│   │   │   │   │   ├── 841e7a26e4eb057b24511e7b92d42b257a80e5
│   │   │   │   │   └── db641593cb80335c37bc39b7a864147c3eb282
│   │   │   │   ├── a4/
│   │   │   │   │   └── f75a1485a7c408fba965e72a42fcf43bfbf661
│   │   │   │   ├── a6/
│   │   │   │   │   └── 344aac8c09253b3b630fb776ae94478aa0275b
│   │   │   │   ├── a9/
│   │   │   │   │   └── 5c4ecf9f7ff70cc4fdb51781c2b435acbb1ea9
│   │   │   │   ├── ad/
│   │   │   │   │   └── 0bcbeb288f0d1373d88e0762e66357f55b8311
│   │   │   │   ├── b2/
│   │   │   │   │   └── 1f41a2331ca83b29b398c03967785fd8ca5f90
│   │   │   │   ├── b3/
│   │   │   │   │   └── c89efc852e22f71eabf5dfbc6ac62493425eb6
│   │   │   │   ├── b7/
│   │   │   │   │   ├── 76ba64681a200a8970ea98856ce256a301b32e
│   │   │   │   │   └── 8979ea6f9ebb70c99285db71b4c79ebdeaf78f
│   │   │   │   ├── b8/
│   │   │   │   │   ├── 5c608bf6fc48dd1d5e5ceee80b37920d873d9b
│   │   │   │   │   └── 9befb20ccf53bd92424dc5f4a0249fe4dbc526
│   │   │   │   ├── bf/
│   │   │   │   │   └── f93d862796105c8cf1a0b3331ad3bec68aee91
│   │   │   │   ├── c3/
│   │   │   │   │   └── a6245340b28b0655f70e78fd546627bd585edd
│   │   │   │   ├── c6/
│   │   │   │   │   └── d6b6f1522c8fcb1fcea5e6cb1ebd4ca6564afe
│   │   │   │   ├── c7/
│   │   │   │   │   └── 6f0ed3432417e3ba1c4188b7e807111b2c54a4
│   │   │   │   ├── d0/
│   │   │   │   │   └── 193716e8eda9731eade78c9bdaea0c2ccd6212
│   │   │   │   ├── dc/
│   │   │   │   │   └── dbc57a77d5ff60662620a72825a053065e70f1
│   │   │   │   ├── dd/
│   │   │   │   │   └── af80a08f610794d9b9359102953351fdf7f674
│   │   │   │   ├── ed/
│   │   │   │   │   └── 1f6233d84bc3e52548de38ae319880ef2fa963
│   │   │   │   ├── f3/
│   │   │   │   │   └── a33423f2688dbc7f8ea178945175dee43e946e
│   │   │   │   ├── f9/
│   │   │   │   │   └── ba8cf65f3e3104dd061c178066ec8247811f33
│   │   │   │   ├── fa/
│   │   │   │   │   └── 308e31a72d6a35eb472623bb1f116b80223a2c
│   │   │   │   ├── info/
│   │   │   │   └── pack/
│   │   │   ├── packed-refs
│   │   │   └── refs/
│   │   │   │   ├── heads/
│   │   │   │   │   └── main
│   │   │   │   ├── remotes/
│   │   │   │   │   └── origin/
│   │   │   │   │   │   └── HEAD
│   │   │   │   └── tags/
│   │   ├── .gitattributes
│   │   ├── CODE_OF_CONDUCT.md
│   │   ├── LICENSE
│   │   ├── README.md
│   │   ├── SECURITY.md
│   │   ├── SUPPORT.md
│   │   ├── config.json
│   │   ├── configuration_florence2.py
│   │   ├── convert_to_safetensors.py
│   │   ├── generation_config.json
│   │   ├── model.safetensors
│   │   ├── modeling_florence2.py
│   │   ├── modeling_florence2.txt
│   │   ├── preprocessor_config.json
│   │   ├── processing_florence2.py
│   │   ├── tokenizer.json
│   │   ├── tokenizer_config.json
│   │   └── vocab.json
│   └── Florence2-large/
│   │   ├── CODE_OF_CONDUCT.md
│   │   ├── LICENSE
│   │   ├── README.md
│   │   ├── SECURITY.md
│   │   ├── SUPPORT.md
│   │   ├── config.json
│   │   ├── configuration_florence2.py
│   │   ├── generation_config.json
│   │   ├── gitattributes
│   │   ├── modeling_florence2.py
│   │   ├── preprocessor_config.json
│   │   ├── processing_florence2.py
│   │   ├── pytorch_model.bin
│   │   ├── tokenizer.json
│   │   ├── tokenizer_config.json
│   │   └── vocab.json
├── output/
│   ├── a-beautiful-scene-of-a-tropical-island-there-are-a_005.jpg
│   ├── a-close-up-of-a-young-girl-with-long-brown-hair-is_000.jpg
│   ├── a-man-is-walking-down-a-runway-wearing-a-long-blue_008.jpg
│   ├── a-robot-is-standing-in-front-of-a-wall-the-robot-i_004.png
│   ├── a-woman-in-a-green-kimono-is-standing-on-a-wooden-_015.jpg
│   ├── a-woman-in-a-white-kimono-is-standing-on-a-bridge-_020.jpg
│   ├── a-woman-in-a-white-kimono-is-standing-on-a-wooden-_017.jpg
│   ├── a-woman-is-standing-in-a-garden-of-roses-she-is-we_019.jpg
│   ├── a-woman-is-standing-in-a-pool-of-water-she-is-wear_006.jpg
│   ├── a-woman-is-standing-in-the-water-she-is-wearing-a-_007.jpg
│   ├── a-woman-is-standing-in-the-water-she-is-wearing-a-_009.jpg
│   ├── a-woman-is-staring-into-the-camera-her-hair-is-wet_010.jpg
│   ├── a-woman-is-wearing-a-black-shiny-outfit-she-has-lo_012.jpg
│   ├── a-woman-is-wearing-a-red-and-white-kimono-she-is-s_003.jpg
│   ├── a-woman-is-wearing-a-red-and-white-kimono-she-is-s_021.jpg
│   ├── a-woman-is-wearing-a-white-and-red-kimono-she-is-s_018.jpg
│   ├── a-woman-is-wearing-a-white-kimono-with-red-flowers_016.jpg
│   ├── a-woman-with-wet-hair-is-looking-directly-into-the_011.jpg
│   ├── an-eye-is-shown-on-a-white-background-the-eye-has-_002.jpg
│   ├── four-people-are-standing-in-a-dark-room-looking-at_013.jpg
│   ├── people-are-walking-in-a-dark-subway-station-there-_014.jpg
│   ├── stockprep_resultados_20250625_035006.json
│   └── this-is-an-animated-image-of-a-girl-the-girl-is-si_001.jpg
├── requirements.txt
├── salida/
├── scrip_prueba.py
├── src/
│   ├── core/
│   │   ├── __init__.py
│   │   ├── __pycache__/
│   │   │   ├── __init__.cpython-311.pyc
│   │   │   ├── image_processor.cpython-311.pyc
│   │   │   └── model_manager.cpython-311.pyc
│   │   ├── batch_engine.py
│   │   ├── image_processor.py
│   │   ├── model_manager.py
│   ├── gui/
│   │   ├── __init__.py
│   │   ├── __pycache__/
│   │   │   ├── __init__.cpython-311.pyc
│   │   │   └── main_window.cpython-311.pyc
│   │   └── main_window.py
│   ├── io/
│   │   └── output_handler.py
│   └── utils/
│   │   └── __init__.py
├── temp/
└── verificar_instalacion.py
```
