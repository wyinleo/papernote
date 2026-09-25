# 单位统计归并

地图、单位排名和学者档案按已核验的上级大学或机构统计；论文详情保持原署名层级。`parent_id` 表示统计归属，`parent_source` 保存证据，不删除原实体。

同一论文出现大学及其多个下属单位时，合并后的论文数与年度分数只计一次。合作边在归并后按论文 ID 去重，同一上级内部的关系不计作跨单位合作。

| 原署名单位 | 统计单位 | 依据 |
| --- | --- | --- |
| 清华大学网络科学与网络空间研究院 | 清华大学 | [官方来源](https://www.insc.tsinghua.edu.cn/) |
| Data61 CSIRO | CSIRO | [官方来源](https://www.csiro.au/en/work-with-us/industries/technology) |
| 中国科学院大学网络空间安全学院 | 中国科学院大学 | [官方来源](https://scs.ucas.ac.cn/) |
| 山东大学网络空间安全学院 | 山东大学 | [官方来源](https://cst.qd.sdu.edu.cn/) |
| MIT Computer Science and Artificial Intelligence Laboratory | Massachusetts Institute of Technology | [官方来源](https://www.csail.mit.edu/about/mission-history) |
| 北京信息科学与技术国家研究中心 | 清华大学 | [官方来源](https://www.bnrist.tsinghua.edu.cn/) |
| 武汉大学国家网络安全学院 | 武汉大学 | [官方来源](https://cse.whu.edu.cn/) |
| COSIC, KU Leuven | KU Leuven | [官方来源](https://www.esat.kuleuven.be/cosic/about-us/) |
| DistriNet, KU Leuven | KU Leuven | [官方来源](https://distrinet.cs.kuleuven.be/) |
| 华中科技大学网络空间安全学院 | 华中科技大学 | [官方来源](https://cse.hust.edu.cn/) |

联合机构、校企联合中心、多机构共同署名和不同校区保留独立记录，待有明确统计口径和证据后再处理。例如香港科技大学（广州）保持独立；中国科学院各研究所不归入中国科学院大学；University of Massachusetts 不直接等同于 Amherst 分校。构建器校验归属循环、不存在的父实体、证据缺失和跨国家归并。
