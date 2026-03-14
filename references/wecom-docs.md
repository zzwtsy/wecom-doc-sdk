# 企业微信文档参考索引

本文档记录当前仓库实现和维护时最常用的企业微信官方文档入口，便于在发布、排查和扩展接口时快速定位来源。

## 固定入口

- 企业微信服务端 API 概述：`https://developer.work.weixin.qq.com/document/path/97392`
- 官方文档链接格式：`https://developer.work.weixin.qq.com/document/path/{category_id}`

## 命名说明

- 仓库本地文档文件名中的前缀通常对应 `doc_id`
- 官方访问链接使用的是 `category_id`
- `doc_id` 与 `category_id` 不是同一概念，不能直接互相替换

## 当前实现相关文档

### 通用

| 用途 | 本地文件 | doc_id | category_id | 官方链接 |
| --- | --- | ---: | ---: | --- |
| 服务端 API 概述 | `docs/企业内部开发/服务端API/文档/43883-概述.md` | 43883 | 97392 | `https://developer.work.weixin.qq.com/document/path/97392` |
| 获取 access_token | `docs/企业内部开发/服务端API/开发指南/15074-获取access_token.md` | 15074 | 91039 | `https://developer.work.weixin.qq.com/document/path/91039` |
| 全局错误码 | `docs/企业内部开发/附录/10649-全局错误码.md` | 10649 | 96213 | `https://developer.work.weixin.qq.com/document/path/96213` |

### 管理智能表格内容

| 用途 | 本地文件 | doc_id | category_id | 官方链接 |
| --- | --- | ---: | ---: | --- |
| 分类入口 | `docs/企业内部开发/服务端API/文档/管理智能表格内容/` | - | 99895 | `https://developer.work.weixin.qq.com/document/path/99895` |
| 添加子表 | `docs/企业内部开发/服务端API/文档/管理智能表格内容/53106-添加子表.md` | 53106 | 100214 | `https://developer.work.weixin.qq.com/document/path/100214` |
| 删除子表 | `docs/企业内部开发/服务端API/文档/管理智能表格内容/53107-删除子表.md` | 53107 | 100215 | `https://developer.work.weixin.qq.com/document/path/100215` |
| 更新子表 | `docs/企业内部开发/服务端API/文档/管理智能表格内容/53108-更新子表.md` | 53108 | 100216 | `https://developer.work.weixin.qq.com/document/path/100216` |
| 查询子表 | `docs/企业内部开发/服务端API/文档/管理智能表格内容/53109-查询子表.md` | 53109 | 101182 | `https://developer.work.weixin.qq.com/document/path/101182` |
| 添加视图 | `docs/企业内部开发/服务端API/文档/管理智能表格内容/53110-添加视图.md` | 53110 | 100217 | `https://developer.work.weixin.qq.com/document/path/100217` |
| 删除视图 | `docs/企业内部开发/服务端API/文档/管理智能表格内容/53111-删除视图.md` | 53111 | 100218 | `https://developer.work.weixin.qq.com/document/path/100218` |
| 查询视图 | `docs/企业内部开发/服务端API/文档/管理智能表格内容/53112-查询视图.md` | 53112 | 101183 | `https://developer.work.weixin.qq.com/document/path/101183` |
| 更新视图 | `docs/企业内部开发/服务端API/文档/管理智能表格内容/53113-更新视图.md` | 53113 | 100219 | `https://developer.work.weixin.qq.com/document/path/100219` |
| 添加字段 | `docs/企业内部开发/服务端API/文档/管理智能表格内容/53114-添加字段.md` | 53114 | 100220 | `https://developer.work.weixin.qq.com/document/path/100220` |
| 删除字段 | `docs/企业内部开发/服务端API/文档/管理智能表格内容/53115-删除字段.md` | 53115 | 100221 | `https://developer.work.weixin.qq.com/document/path/100221` |
| 更新字段 | `docs/企业内部开发/服务端API/文档/管理智能表格内容/53116-更新字段.md` | 53116 | 100222 | `https://developer.work.weixin.qq.com/document/path/100222` |
| 查询字段 | `docs/企业内部开发/服务端API/文档/管理智能表格内容/53117-查询字段.md` | 53117 | 101184 | `https://developer.work.weixin.qq.com/document/path/101184` |
| 添加记录 | `docs/企业内部开发/服务端API/文档/管理智能表格内容/53118-添加记录.md` | 53118 | 100224 | `https://developer.work.weixin.qq.com/document/path/100224` |
| 删除记录 | `docs/企业内部开发/服务端API/文档/管理智能表格内容/53119-删除记录.md` | 53119 | 100225 | `https://developer.work.weixin.qq.com/document/path/100225` |
| 更新记录 | `docs/企业内部开发/服务端API/文档/管理智能表格内容/53120-更新记录.md` | 53120 | 100226 | `https://developer.work.weixin.qq.com/document/path/100226` |
| 查询记录 | `docs/企业内部开发/服务端API/文档/管理智能表格内容/53121-查询记录.md` | 53121 | 101185 | `https://developer.work.weixin.qq.com/document/path/101185` |
| 添加编组 | `docs/企业内部开发/服务端API/文档/管理智能表格内容/59536-添加编组.md` | 59536 | 101178 | `https://developer.work.weixin.qq.com/document/path/101178` |
| 更新编组 | `docs/企业内部开发/服务端API/文档/管理智能表格内容/59537-更新编组.md` | 59537 | 101180 | `https://developer.work.weixin.qq.com/document/path/101180` |
| 删除编组 | `docs/企业内部开发/服务端API/文档/管理智能表格内容/59538-删除编组.md` | 59538 | 101179 | `https://developer.work.weixin.qq.com/document/path/101179` |
| 获取编组 | `docs/企业内部开发/服务端API/文档/管理智能表格内容/59539-获取编组.md` | 59539 | 101181 | `https://developer.work.weixin.qq.com/document/path/101181` |

## 维护建议

- 新增接口封装时，同步在本文件补充对应官方文档条目
- 如果本地文档文件名与官方链接无法直接对应，优先补齐 `doc_id -> category_id` 映射
- 如官方文档入口调整，以本文件中的官方链接为首要同步对象
