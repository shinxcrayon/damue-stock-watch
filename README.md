# DAMUE 在庫復活通知Bot（5600-Fog Silver）

DAMUE ONLINE STORE の商品「5600-Fog Silver」が売り切れ→在庫ありに
変化したタイミングで、あなたのLINEに自動通知するBotです。

**毎週金曜 17:30〜19:00（日本時間）**の間、**1分おき**に自動でチェック
し、在庫が復活したタイミングでLINEにメッセージを送ります（決済の自動
実行は行いません。通知を受けたらご自身でカートに入れて購入してくだ
さい）。

---

## 1. LINE公式アカウントを作成する（無料）

1. [LINE Official Account Manager](https://www.linebiz.com/jp/entry/) にアクセスし、
   個人利用として無料でアカウントを開設します。
2. 開設後、管理画面（LINE Official Account Manager）にログインします。

## 2. Messaging APIを有効化してトークンを発行する

1. 管理画面の「設定」→「Messaging API」タブを開き、「Messaging APIを利用する」を有効化します。
2. 同じ画面で「チャンネルアクセストークン（長期）」を発行し、表示された文字列をコピーしておきます。
   （これが `LINE_CHANNEL_ACCESS_TOKEN` になります）
3. 応答メッセージ等はオフにしておいてOKです（通知専用のBotとして使うため）。

## 3. 自分のLINEでこの公式アカウントを友だち追加する

- 管理画面に表示されるQRコードを、自分のLINEアプリで読み取って友だち追加します。
- ブロードキャスト配信（友だち全員への一斉送信）を使う仕組みなので、
  友だちになっているのが自分だけであれば、実質「自分専用の通知」になります。

## 4. GitHubにリポジトリを作成してコードを配置する

1. GitHubで新しいリポジトリを作成します（Private推奨）。
2. このフォルダ一式（`check_stock.py` / `.github/workflows/check-stock.yml` /
   `stock_state.json` / `README.md`）をそのままアップロード（push）します。
   フォルダ構成を変えないよう注意してください。

## 5. トークンをGitHub Secretsに登録する

1. リポジトリの `Settings` → `Secrets and variables` → `Actions` を開きます。
2. `New repository secret` をクリックし、以下を登録します。
   - Name: `LINE_CHANNEL_ACCESS_TOKEN`
   - Value: 手順2でコピーしたトークン

## 6. 動作確認

1. リポジトリの `Actions` タブを開き、ワークフローが表示されていることを確認します
   （表示されない場合はActionsを有効化してください）。
2. `Check DAMUE Stock` ワークフローを選び、`Run workflow` から手動実行してみます。
3. ログに `previous_available=... current_available=...` と表示されれば正常に動作しています。
4. 在庫が復活すると、自動でLINEにメッセージが届きます。

---

## 補足

- 監視対象は**毎週金曜 17:30〜19:00（日本時間）、1分間隔**です。
  GitHub Actionsの`cron`は5分未満の間隔を安定して扱えないため、
  17:20（JST）に1回だけジョブを起動し、そのジョブ内部でPythonが
  19:00まで1分おきにループしながらチェックし続ける方式にしています
  （`.github/workflows/check-stock.yml` の起動時刻と、
  `check_stock.py` 冒頭の `CHECK_INTERVAL_SECONDS` / `WATCH_START` /
  `WATCH_END` が対応しています）。
- ジョブは最大120分のタイムアウトを設定しており、17:20開始〜19:00終了
  （約100分）+ スケジューラの遅延バッファを見込んでいます。
- チェック間隔をさらに短くしたい場合は `CHECK_INTERVAL_SECONDS` を、
  監視時間帯を変えたい場合は `WATCH_WEEKDAY` / `WATCH_START` /
  `WATCH_END` と、ワークフローの起動時刻（cron）の両方を合わせて
  書き換えてください。
- 在庫判定はShopifyストア標準の商品JSON
  （`https://damue.jp/products/5600-fog-silver.json`）を参照しており、
  ページのデザイン変更の影響を受けにくい作りになっています。
- Messaging APIの無料枠は月200通です。状態が変化したときだけ送信する
  仕組みなので、通常の使い方であれば十分収まります。
- 別の商品も監視したい場合は、`check_stock.py` 冒頭の `PRODUCT_HANDLE`
  （URLの `/products/` の後ろの部分）を書き換えれば流用できます。
- **決済の自動化は行いません。** 規約違反や不正購入のリスクがあるため、
  在庫復活の通知までを自動化し、購入操作はご自身で行ってください。
