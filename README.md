# Gemini API 负载均衡器 (gemini-balance-do)

> 这是一个部署在 Cloudflare Workers 上的 Gemini API 负载均衡器和代理服务，使用了 Durable Objects 来存储和管理 API 密钥，无论你连接的 worker 节点在属于哪个地区，最后都会转发到美国以后再向 Gemini 发起请求，不用再担心地区不支持的问题！

它旨在解决以下问题：
*   将多个 Gemini API 密钥聚合到一个端点中。
*   通过随机轮询密钥池来实现请求的负载均衡。
*   提供与 OpenAI API 兼容的接口，使现有工具可以轻松集成。

## ✨ 主要功能

*   **Gemini API 代理**: 作为 Google Gemini API 的稳定代理。
*   **负载均衡**: 在配置的多个 API 密钥之间随机分配请求。
*   **本地 key 透传**：如果不想使用多 key 负载均衡，可以开启本地 key 透传，此时本项目仅作为一个 Gemini API 中转
*   **OpenAI API 格式兼容**: 支持 `/v1/chat/completions`, `/v1/embeddings` 和 `/v1/models` 等常用 OpenAI 端点。
*   **流式响应**: 完全支持 Gemini API 的流式响应。
*   **API 密钥管理**:
    *   提供一个简单的 Web UI 用于批量添加和查看 API 密钥。
    *   提供 API 接口用于检查并自动清理失效的密钥。
*   **持久化存储**: 使用 Cloudflare Durable Objects 内的 SQLite 安全地存储 API 密钥。

## 🚀 部署

你可以通过以下两种方式将此项目部署到你自己的 Cloudflare 账户：

### 方法一：通过 Wrangler CLI 部署

1.  **克隆项目**
    ```bash
    git clone https://github.com/zaunist/gemini-balance-do.git
    cd gemini-balance-do
    ```

2.  **安装依赖**
    ```bash
    pnpm install
    ```

3.  **登录 Wrangler**
    ```bash
    npx wrangler login
    ```

4.  **部署到 Cloudflare**
    ```bash
    pnpm run deploy
    ```
    部署成功后，Wrangler 会输出你的 Worker URL。

### 方法二：通过 Cloudflare Dashboard 部署 (推荐)

1.  **Fork 项目**: 点击本仓库右上角的 "Fork" 按钮，将此项目复刻到你自己的 GitHub 账户。

2.  **登录 Cloudflare**: 打开 [Cloudflare Dashboard](https://dash.cloudflare.com/)。

3.  **创建 Worker**:
    *   在左侧导航栏中，进入 `Workers & Pages`。
    *   点击 `创建应用程序` -> `连接到 Git`。
    *   选择你刚刚 Fork 的仓库。
    *   在“构建和部署”设置中，Cloudflare 通常会自动检测到这是一个 Worker 项目，无需额外配置。
    *   点击 `保存并部署`。

## 🔑 API 密钥管理

部署完成后，你可以通过访问你的 Worker URL 来管理 Gemini API 密钥。

*   **访问管理面板**: 在浏览器中打开你的 Worker URL (例如 `https://gemini-balance-do.your-worker.workers.dev`)，首次访问会显示登录框，需要输入你的 HOME_ACCESS_KEY 进行认证，认证通过后才能进入管理页面。
*   **批量添加密钥**: 在文本框中输入你的 Gemini API 密钥，每行一个，然后点击“添加密钥”。
*   **查看和刷新**: 在右侧面板可以查看已存储的密钥，并可以点击“刷新”按钮更新列表。
*   **一键检查**： 点击“一键检查”按钮，可以检查 API key 可用性。
*   **批量删除**： 选中无效的 API key，可以一键删除所有无效的 API key。

## 配置

`FORWARD_CLIENT_KEY_ENABLED` : 默认为 false，设置为 true 时，会透传客户端的 key，此时仅作为 Gemini API 代理，没有多 key 负载均衡功能。

`AUTH_KEY` ： 默认为：`ajielu`，本项目API请求密钥，如果 `FORWARD_CLIENT_KEY_ENABLED` 为 true，那么本项目仅作为一个 Gemini API 代理，无需认证

**注意**：当启用 `FORWARD_CLIENT_KEY_ENABLED` 时，客户端的 API key 可以通过以下方式传递：
- 查询参数：`?key=your_api_key`
- Header：`x-goog-api-key: your_api_key`
- Authorization Header：`Authorization: Bearer your_api_key`

`HOME_ACCESS_KEY`：网页管理面板密码，默认为 `7b18e536c27ab304266db3220b8e000db8fbbe35d6e1fde729a1a1d47303858d`

**强烈建议你在Cloudflare Worker环境变量中修改 `HOME_ACCESS_KEY` 和 `AUTH_KEY` 的值，修改完成后重新部署即可。**

## 💻 API 用法

使用方式，在 AI 客户端中，填入以下配置：

BaseURL: <你的worker地址>

API 密钥: `<你的AUTH_KEY>`，如果设置了 `FORWARD_CLIENT_KEY_ENABLED` 为 true，那么这里需要填你自己的 key 就行

### 管理 API

所有管理 API 均需在请求头添加 `Authorization: Bearer <你的HOME_ACCESS_KEY>` 或自动携带 cookie `auth-key` 进行认证：

*   `GET /api/keys`: 获取所有已存储的 API 密钥。
*   `POST /api/keys`: 批量添加 API 密钥。请求体为 `{"keys": ["key1", "key2"]}`。
*   `GET /api/keys/check`: 检查所有密钥的有效性。
*   `DELETE /api/keys`: 批量删除 API 密钥。请求体为 `{"keys": ["key1", "key2"]}`。

普通 Gemini/OpenAI API 调用只需使用 `AUTH_KEY`，无需管理权限认证

## Gemini 3 预览支持与用法

项目已内置 Gemini 3 预览型号列表，OpenAI 兼容的 `/v1/models` 会返回：

- `gemini-3-pro-preview`
- `gemini-3-flash-preview`
- `gemini-3-pro-image-preview`

同时透传了新版的思考配置、工具配置、图像生成配置与媒体分辨率配置，方便客户端直接使用官方 SDK。

### 使用 @google/genai（Node/Browser）

```ts
import { GoogleGenAI } from "@google/genai";

const ai = new GoogleGenAI({
  // 可选：指定 API 版本（默认 v1beta，媒体分辨率需 v1alpha）
  apiVersion: "v1beta",
  // 如果使用本项目的 AUTH_KEY 模式，请在请求里带上 Authorization: Bearer <AUTH_KEY>
});

async function run() {
  const response = await ai.models.generateContent({
    model: "gemini-3-pro-preview",
    contents: "How does AI work?",
    config: {
      // 思考级别：low / medium / high（自动映射到 thinkingBudget）
      thinkingConfig: { thinkingLevel: "low" },
    },
  });

  console.log(response.text);
}

run();
```

### 思考级别（thinking level）

- 支持字段：`thinkingConfig`, `thinking_config`, `thinkingLevel`, `thinking_level`，以及 OpenAI 风格的 `reasoning_effort`（low/medium/high）。
- 服务端会合并到 `generationConfig.thinkingConfig` 并补全 `thinkingBudget` 兼容旧字段。

### 媒体分辨率（需要 v1alpha）

```ts
const ai = new GoogleGenAI({ apiVersion: "v1alpha" });

await ai.models.generateContent({
  model: "gemini-3-pro-preview",
  contents: [
    {
      parts: [
        { text: "What is in this image?" },
        {
          inlineData: { mimeType: "image/jpeg", data: "<base64>" },
          mediaResolution: { level: "media_resolution_high" }, // 关键字段
        },
      ],
    },
  ],
});
```

如果检测到 `mediaResolution`，代理会自动切换到 `v1alpha`，也可以显式传 `apiVersion`。

### 工具与响应模式（googleSearch / urlContext / JSON schema）

```ts
import { GoogleGenAI } from "@google/genai";
import { z } from "zod";
import { zodToJsonSchema } from "zod-to-json-schema";

const ai = new GoogleGenAI({});

const matchSchema = z.object({
  winner: z.string(),
  final_match_score: z.string(),
  scorers: z.array(z.string()),
});

const response = await ai.models.generateContent({
  model: "gemini-3-pro-preview",
  contents: "Search for all details for the latest Euro.",
  config: {
    tools: [{ googleSearch: {} }, { urlContext: {} }],
    responseMimeType: "application/json",
    responseJsonSchema: zodToJsonSchema(matchSchema),
  },
});
```

- `config.tools` 会被透传；如果请求或模型包含 `-search-preview`/`:search`，会自动追加 `googleSearch`。
- `responseMimeType`/`responseJsonSchema`、`responseSchema` 均可传递。

### 图像生成（gemini-3-pro-image-preview）

```ts
import { GoogleGenAI } from "@google/genai";
import * as fs from "node:fs";

const ai = new GoogleGenAI({});

const response = await ai.models.generateContent({
  model: "gemini-3-pro-image-preview",
  contents: "Generate a visualization of the current weather in Tokyo.",
  config: {
    tools: [{ googleSearch: {} }], // 可选
    imageConfig: { aspectRatio: "16:9", imageSize: "4K" },
  },
});

for (const part of response.candidates[0].content.parts) {
  if (part.inlineData) {
    fs.writeFileSync("weather_tokyo.png", Buffer.from(part.inlineData.data, "base64"));
  }
}
```

> 提示：如果启用了 `FORWARD_CLIENT_KEY_ENABLED=true`，上述示例中的 `GoogleGenAI` 需直接传入你的 Google API Key；否则使用本服务的 `AUTH_KEY` 走负载均衡。


## 感谢

- [gemini-balance-lite](https://github.com/tech-shrimp/gemini-balance-lite)

- [cloudflare](https://www.cloudflare.com/)
