# 地图来源

国界底图：Natural Earth `ne_110m_admin_0_countries`，公共领域。
https://github.com/nvkelso/natural-earth-vector/blob/master/geojson/ne_110m_admin_0_countries.geojson
https://www.naturalearthdata.com/about/terms-of-use/

`world-map.js` 为等距圆柱投影（经纬度线性投影），不绘制南极洲；新加坡以标记补充。位置标记是国家级示意位置，不代表单位地址。国界沿用底图，仅用于研究分布展示。

单位国家代码在 `papers/entity_registry.json` 的 `country_code` 中维护，经构建器输出；分校使用该分校所在地。跨国企业、独立研究者和无法确定所在地的单位暂不映射，页面显示缺失数量。请用论文中的实际单位地址核验后再补录，不按作者姓名或企业总部推断。
