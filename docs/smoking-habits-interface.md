# 喫煙習慣フォーム インターフェース仕様書

## 概要

本書は、喫煙習慣に関する情報を収集するフォームのフロントエンドおよびバックエンドインターフェース仕様を定義します。

## 1. フォーム項目設計

### 1.1 基本項目

| 項目名 | フィールド名 | 型 | 必須 | 説明 | 選択肢/範囲 |
|--------|-------------|-----|------|------|-------------|
| 現在の喫煙状況 | smoking_status | string | ✓ | 現在の喫煙状況 | "smoker", "non_smoker", "ex_smoker" |
| 1日の喫煙本数 | daily_cigarettes | number | 条件付き | 1日あたりの喫煙本数 | 1-100 (smoking_status="smoker"の場合必須) |
| 喫煙年数 | smoking_years | number | 条件付き | 喫煙していた/している年数 | 1-80 (smoking_status="smoker"または"ex_smoker"の場合必須) |
| 禁煙開始時期 | quit_date | string | 条件付き | 禁煙した年月 | YYYY-MM形式 (smoking_status="ex_smoker"の場合必須) |
| タバコの種類 | cigarette_type | string | 条件付き | 使用するタバコの種類 | "traditional", "electronic", "both" (smoking_status="smoker"の場合必須) |
| タール含有量 | tar_content | number | 任意 | タール含有量（mg） | 1-25 |
| ニコチン含有量 | nicotine_content | number | 任意 | ニコチン含有量（mg） | 0.1-3.0 |

### 1.2 追加項目（将来拡張）

| 項目名 | フィールド名 | 型 | 必須 | 説明 | 選択肢/範囲 |
|--------|-------------|-----|------|------|-------------|
| 禁煙意向 | quit_intention | string | 任意 | 禁煙への意向 | "planning", "considering", "not_interested" |
| 一日の喫煙パターン | smoking_pattern | array | 任意 | 喫煙時間帯 | ["morning", "afternoon", "evening", "night"] |

## 2. API仕様

### 2.1 エンドポイント情報

- **URL**: `POST /api/v1/smoking-habits`
- **Content-Type**: `application/json`
- **認証**: Bearer Token（Firebase Authentication）

### 2.2 リクエスト仕様

#### リクエストヘッダー

```
Authorization: Bearer <firebase_id_token>
Content-Type: application/json
```

#### リクエストボディ

```json
{
  "session_id": "string (optional)",
  "smoking_status": "smoker | non_smoker | ex_smoker",
  "daily_cigarettes": "number (conditional)",
  "smoking_years": "number (conditional)", 
  "quit_date": "string (conditional)",
  "cigarette_type": "traditional | electronic | both (conditional)",
  "tar_content": "number (optional)",
  "nicotine_content": "number (optional)",
  "quit_intention": "planning | considering | not_interested (optional)",
  "smoking_pattern": "array of strings (optional)"
}
```

#### パターン別リクエスト例

**非喫煙者の場合:**
```json
{
  "session_id": "sess_abc123",
  "smoking_status": "non_smoker"
}
```

**現在喫煙者の場合:**
```json
{
  "session_id": "sess_abc123", 
  "smoking_status": "smoker",
  "daily_cigarettes": 15,
  "smoking_years": 8,
  "cigarette_type": "traditional",
  "tar_content": 12,
  "nicotine_content": 1.2,
  "quit_intention": "considering",
  "smoking_pattern": ["morning", "evening"]
}
```

**元喫煙者の場合:**
```json
{
  "session_id": "sess_abc123",
  "smoking_status": "ex_smoker", 
  "smoking_years": 5,
  "quit_date": "2023-06",
  "cigarette_type": "traditional",
  "tar_content": 10,
  "nicotine_content": 1.0
}
```

### 2.3 レスポンス仕様

#### 成功レスポンス (200 OK)

```json
{
  "success": true,
  "data": {
    "questionnaire_id": "quest_def456",
    "session_id": "sess_abc123",
    "submitted_at": "2024-01-15T10:30:00Z",
    "smoking_habits": {
      "smoking_status": "smoker",
      "daily_cigarettes": 15,
      "smoking_years": 8,
      "cigarette_type": "traditional",
      "tar_content": 12,
      "nicotine_content": 1.2,
      "quit_intention": "considering",
      "smoking_pattern": ["morning", "evening"]
    }
  }
}
```

#### エラーレスポンス

**バリデーションエラー (400 Bad Request):**
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "入力データに不正があります",
    "details": [
      {
        "field": "daily_cigarettes", 
        "message": "喫煙者の場合、1日の喫煙本数は必須です"
      },
      {
        "field": "smoking_years",
        "message": "喫煙年数は1以上80以下で入力してください"
      }
    ]
  }
}
```

**認証エラー (401 Unauthorized):**
```json
{
  "success": false,
  "error": {
    "code": "AUTHENTICATION_ERROR", 
    "message": "認証が必要です"
  }
}
```

**サーバーエラー (500 Internal Server Error):**
```json
{
  "success": false,
  "error": {
    "code": "INTERNAL_ERROR",
    "message": "内部サーバーエラーが発生しました"
  }
}
```

## 3. データバリデーション

### 3.1 バリデーションルール

#### 必須項目バリデーション

- `smoking_status`: 必須、列挙値チェック
- `daily_cigarettes`: smoking_status="smoker"の場合必須、1-100の範囲
- `smoking_years`: smoking_status="smoker"または"ex_smoker"の場合必須、1-80の範囲
- `quit_date`: smoking_status="ex_smoker"の場合必須、YYYY-MM形式
- `cigarette_type`: smoking_status="smoker"の場合必須、列挙値チェック

#### 値範囲バリデーション

- `daily_cigarettes`: 1-100
- `smoking_years`: 1-80  
- `tar_content`: 1-25
- `nicotine_content`: 0.1-3.0
- `quit_date`: 現在の年月以前

#### 論理整合性バリデーション

- 禁煙日が現在より未来でないこと
- 喫煙年数が利用者の年齢を超えないこと（年齢情報がある場合）

### 3.2 エラーメッセージ

| エラーコード | メッセージ | 詳細 |
|-------------|------------|------|
| REQUIRED_FIELD | {field}は必須項目です | 必須項目未入力 |
| INVALID_ENUM | {field}の値が不正です | 列挙値以外の値 |
| OUT_OF_RANGE | {field}は{min}以上{max}以下で入力してください | 数値範囲外 |
| INVALID_FORMAT | {field}の形式が正しくありません | 日付形式等の不正 |
| LOGICAL_ERROR | {message} | 論理的矛盾 |

## 4. フロントエンド実装

### 4.1 TypeScript型定義

#### 基本型定義

```typescript
// 喫煙状況の列挙型
export type SmokingStatus = 'smoker' | 'non_smoker' | 'ex_smoker';

// タバコの種類の列挙型  
export type CigaretteType = 'traditional' | 'electronic' | 'both';

// 禁煙意向の列挙型
export type QuitIntention = 'planning' | 'considering' | 'not_interested';

// 喫煙パターンの列挙型
export type SmokingPatternItem = 'morning' | 'afternoon' | 'evening' | 'night';

// 喫煙習慣データ型
export interface SmokingHabitsData {
  session_id?: string;
  smoking_status: SmokingStatus;
  daily_cigarettes?: number;
  smoking_years?: number;
  quit_date?: string; // YYYY-MM形式
  cigarette_type?: CigaretteType;
  tar_content?: number;
  nicotine_content?: number;
  quit_intention?: QuitIntention;
  smoking_pattern?: SmokingPatternItem[];
}
```

#### API型定義

```typescript
// API リクエスト型
export interface SmokingHabitsRequest extends SmokingHabitsData {}

// API レスポンス型
export interface SmokingHabitsResponse {
  success: true;
  data: {
    questionnaire_id: string;
    session_id: string;
    submitted_at: string;
    smoking_habits: SmokingHabitsData;
  };
}

// API エラーレスポンス型
export interface SmokingHabitsError {
  success: false;
  error: {
    code: string;
    message: string;
    details?: Array<{
      field: string;
      message: string;
    }>;
  };
}
```

#### バリデーション型定義

```typescript
// バリデーション結果型
export interface ValidationResult {
  isValid: boolean;
  errors: Array<{
    field: keyof SmokingHabitsData;
    message: string;
  }>;
}

// フォーム状態型
export interface SmokingHabitsFormState extends SmokingHabitsData {
  isSubmitting: boolean;
  errors: Record<keyof SmokingHabitsData, string>;
}
```

### 4.2 APIクライアント実装

```typescript
export class SmokingHabitsApi {
  private baseUrl = '/api/v1';
  
  async submitSmokingHabits(
    data: SmokingHabitsRequest,
    authToken: string
  ): Promise<SmokingHabitsResponse> {
    const response = await fetch(`${this.baseUrl}/smoking-habits`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authToken}`
      },
      body: JSON.stringify(data)
    });

    const result = await response.json();
    
    if (!response.ok) {
      throw new SmokingHabitsApiError(result);
    }
    
    return result;
  }
}

export class SmokingHabitsApiError extends Error {
  constructor(public errorResponse: SmokingHabitsError) {
    super(errorResponse.error.message);
    this.name = 'SmokingHabitsApiError';
  }
}
```

## 5. 既存システムとの連携

### 5.1 セッション管理

- `session_id`により画像アップロードセッションと連携
- 既存の`UploadImageResponse.data.session_id`を使用

### 5.2 AIエンジンとの連携  

- 診断エンジンに`smoking_habits`データを渡す
- `POST /api/v1/generate-prediction`の入力データに含める

### 5.3 結果表示との連携

- 診断結果表示時に喫煙習慣情報も表示
- `GET /api/v1/result/{id}`のレスポンスに含める

## 6. 拡張性

### 6.1 項目追加

- 新しい項目は任意項目として追加
- バックエンドの型定義とバリデーションを拡張
- フロントエンドのフォームコンポーネントを更新

### 6.2 他の健康項目との統合

- 飲酒習慣、運動習慣等の項目追加を想定
- 共通インターフェースパターンの活用
- モジュラー設計による柔軟な拡張

## 7. セキュリティ考慮事項

### 7.1 データ保護

- 個人の健康情報として適切な暗号化
- 保存期間の制限（処理完了後30日）
- アクセスログの記録

### 7.2 入力値検証

- サーバーサイドでの完全な検証
- SQLインジェクション対策
- XSS対策（フロントエンド表示時）

## 8. パフォーマンス考慮事項

### 8.1 レスポンス時間

- 目標応答時間: 500ms以内
- データベースインデックス最適化
- キャッシュ機能の活用

### 8.2 データサイズ

- リクエストサイズ: 5KB以内
- レスポンスサイズ: 10KB以内
- 不要データの除外