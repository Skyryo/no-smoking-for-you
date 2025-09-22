# エージェント実装戦略設計書（PoC 版）

## **1. 全体アーキテクチャ**

### **1.1 エージェント階層構造**

```
root_agent (SequentialAgent)
├── parallel_analysis_agent (ParallelAgent)
│   ├── questionnaire_agent (LlmAgent)
│   └── image_analysis_agent (LlmAgent)
├── image_generation_agent (LlmAgent)
└── report_generator_agent (LlmAgent)
```

### **1.2 実行フロー**

1. **並列分析フェーズ**: 問診データ分析 + 顔画像分析（同時実行）
2. **画像生成フェーズ**: 分析結果を基に 20 年後画像生成
3. **レポート生成フェーズ**: 全結果を統合してユーザー向けレポート作成

## **2. 各エージェントの詳細設計**

### **2.1 ルートエージェント（オーケストレーター）**

```python
root_agent = SequentialAgent(
    name="HealthVisualizationOrchestrator",
    description="健康予測画像生成システムのメインオーケストレーター",
    sub_agents=[
        parallel_analysis_agent,
        image_generation_agent,
        report_generator_agent
    ]
)
```

**責務**:

- 全体の実行順序制御
- エージェント間の状態受け渡し管理
- PoC 用の基本エラーハンドリング

### **2.2 並列分析エージェント**

```python
parallel_analysis_agent = ParallelAgent(
    name="ParallelAnalysisAgent",
    description="問診データと画像データの並列分析",
    sub_agents=[questionnaire_agent, image_analysis_agent]
)
```

**責務**:

- 問診分析と画像分析の同時実行制御
- 実行完了の待機とデータ収集

### **2.3 問診診断エージェント**

```python
questionnaire_agent = LlmAgent(
    name="QuestionnaireAnalyzer",
    model="gemini-2.0-flash",
    description="問診データから健康リスクを分析",
    instruction="""
    あなたは医療データ分析の専門家です。
    提供された問診データを分析し、以下の項目について評価してください：

    1. 生活習慣リスク（食事、運動、睡眠、喫煙、飲酒）
    2. 既往歴・家族歴に基づくリスク
    3. 将来の健康予測（20年後想定）

    結果は以下のJSON形式で出力してください：
    {
        "lifestyle_risks": ["リスク1", "リスク2"],
        "medical_history_risks": ["リスク1", "リスク2"],
        "future_health_prediction": {
            "skin_condition": "良好/普通/要注意",
            "overall_health": "良好/普通/要注意",
            "specific_concerns": ["懸念事項1", "懸念事項2"]
        }
    }
    """,
    tools=[questionnaire_analysis_tool],
    output_key="questionnaire_results"
)
```

**責務**:

- 問診データの構造化分析
- 健康リスク評価
- 20 年後予測のための基礎データ生成

### **2.4 画像診断エージェント**

```python
image_analysis_agent = LlmAgent(
    name="ImageAnalyzer",
    model="gemini-2.0-flash",
    description="顔画像から健康関連特徴量を抽出",
    instruction="""
    あなたは画像解析の専門家です。
    提供された顔画像を分析し、以下の特徴量を抽出してください：

    1. 肌の状態（色調、質感、しわ、シミなど）
    2. 顔の構造的特徴
    3. 年齢推定と老化傾向

    結果は以下のJSON形式で出力してください：
    {
        "skin_analysis": {
            "tone": "明るい/普通/暗い",
            "texture": "滑らか/普通/粗い",
            "aging_signs": ["特徴1", "特徴2"]
        },
        "facial_features": {
            "face_shape": "丸型/楕円型/四角型/逆三角型",
            "estimated_age": 30,
            "aging_progression": "緩やか/標準/早い"
        }
    }
    """,
    tools=[image_analysis_tool],
    output_key="image_analysis_results"
)
```

**責務**:

- 顔画像の特徴量抽出
- 現在の老化状態評価
- 20 年後変化予測のベースライン設定

### **2.5 画像生成エージェント**

```python
image_generation_agent = LlmAgent(
    name="ImageGenerator",
    model="gemini-2.0-flash",
    description="分析結果を基に20年後の顔画像を生成",
    instruction="""
    あなたは画像生成の専門家です。
    問診分析結果（questionnaire_results）と画像分析結果（image_analysis_results）を統合し、
    20年後の顔画像生成のためのプロンプトを作成してください。

    考慮要素：
    1. 自然な老化プロセス
    2. 生活習慣による影響
    3. 健康状態による外見への影響

    以下のJSON形式で出力してください：
    {
        "generation_prompt": "詳細な画像生成プロンプト",
        "generation_parameters": {
            "aging_factor": 0.7,
            "health_impact": "positive/neutral/negative",
            "style": "realistic"
        },
        "generated_image_url": "生成された画像のURL"
    }
    """,
    tools=[image_generation_tool],
    output_key="generated_image_results"
)
```

**責務**:

- 分析結果の統合と解釈
- 画像生成プロンプトの作成
- 実際の画像生成実行

### **2.6 レポート生成エージェント**

```python
report_generator_agent = LlmAgent(
    name="ReportGenerator",
    model="gemini-2.0-flash",
    description="全結果を統合してユーザー向けレポートを生成",
    instruction="""
    あなたはヘルスレポートの専門家です。
    以下の分析結果を統合し、ユーザーに分かりやすいレポートを作成してください：

    - questionnaire_results: 問診分析結果
    - image_analysis_results: 画像分析結果
    - generated_image_results: 生成画像結果

    レポートには以下を含めてください：
    1. 現在の健康状態サマリー
    2. 20年後の予測結果
    3. 改善のための具体的アドバイス
    4. 生成画像の説明

    親しみやすく、モチベーションを向上させる文調で作成してください。
    """,
    output_key="final_report"
)
```

**責務**:

- 全分析結果の統合
- ユーザーフレンドリーなレポート生成
- 改善アドバイスの提供

## **3. ツール実装仕様**

### **3.1 問診分析ツール**

```python
def questionnaire_analysis_tool(questionnaire_data: dict) -> dict:
    """
    問診データを構造化して分析

    Args:
        questionnaire_data: 問診回答データ

    Returns:
        分析結果の辞書
    """
    # PoC用の簡易実装
    # 実際のロジックは問診項目に応じて実装
    pass
```

### **3.2 画像分析ツール**

```python
def image_analysis_tool(image_path: str) -> dict:
    """
    顔画像の特徴量抽出

    Args:
        image_path: 画像ファイルパス

    Returns:
        分析結果の辞書
    """
    # PoC用: OpenCV + MediaPipeまたは外部APIを使用
    pass
```

### **3.3 画像生成ツール**

```python
def image_generation_tool(prompt: str, parameters: dict) -> str:
    """
    20年後画像の生成

    Args:
        prompt: 生成プロンプト
        parameters: 生成パラメータ

    Returns:
        生成画像のURL
    """
    # PoC用: DALL-E、Midjourney API、またはStable Diffusionを使用
    pass
```

## **4. 状態管理設計**

### **4.1 状態キー定義**

```python
# 状態管理用のキー定数
STATE_KEYS = {
    "QUESTIONNAIRE_RESULTS": "questionnaire_results",
    "IMAGE_ANALYSIS_RESULTS": "image_analysis_results",
    "GENERATED_IMAGE_RESULTS": "generated_image_results",
    "FINAL_REPORT": "final_report"
}
```

### **4.2 データフロー**

```
Input: questionnaire_data + face_image
    ↓
[ParallelAgent]
    ├── questionnaire_results (JSON)
    └── image_analysis_results (JSON)
    ↓
[ImageGenerator]
    → generated_image_results (JSON + URL)
    ↓
[ReportGenerator]
    → final_report (Markdown/HTML)
```

## **5. 実装優先順位**

### **Phase 1: コア機能実装**

1. 各 LlmAgent の基本実装
2. シンプルなツール関数の実装（モック含む）
3. SequentialAgent + ParallelAgent の組み合わせテスト

### **Phase 2: 統合テスト**

1. エンドツーエンドフローの動作確認
2. 状態管理の動作確認
3. ADK Web UI での動作テスト

### **Phase 3: 精度向上**

1. プロンプトエンジニアリング
2. ツール機能の改善
3. 出力フォーマットの調整

## **6. 実装時の注意点**

### **6.1 ADK 固有の実装ポイント**

- `output_key`を使用した自動状態保存の活用
- `InvocationContext`による状態共有の確認
- エージェント間での JSON 形式データ受け渡し

### **6.2 PoC 用の簡略化方針**

- エラーハンドリングは基本的なもののみ
- 外部 API の制限やレート制限は考慮しない
- データ永続化は実装しない（セッション内のみ）
- セキュリティ機能は最低限

### **6.3 テストデータ準備**

- サンプル問診データ（JSON 形式）
- テスト用顔画像（複数パターン）
- 期待結果の例

この設計に従って実装することで、ADK の機能を適切に活用しながら、ブレのない一貫した PoC システムを構築できます。
