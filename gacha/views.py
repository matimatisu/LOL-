import random
import requests
from django.shortcuts import render, redirect
from .forms import FiveSummonerForm

# トロールネタ:レアリティで定義
TROLLS = [
    ("ワードを一切置かない。", "コモン", "all"),
    ("3分毎にミッドレーンに集合する。", "コモン", "all"),
    ("ブーツ購入不可", "アンコモン", "all"),
    ("買い物はサポートアイテムのみ。", "アンコモン", "sup"),
    ("ドラゴン・バロンは絶対触らない。", "レア", "lane"),  # lane = jg以外
    ("リコール禁止。", "スーパーレア", "all"),
    ("常に敵ジャングルでファームする。", "スーパーレア", "jg"),
    ("絶対にサモナースペルを使わない。", "ウルトラレア", "lane"), # jg以外
    ("カル三つ購入", "ウルトラレア", "all"),
    ("ポーション購入不可", "レア", "all"),
    ("イグゾースト・クレンズ固定", "コモン", "lane"), # jg以外
    ("オラクルなし", "コモン", "all"),
    ("素材アイテム高いものから購入", "コモン", "all"),
    ("ワード壊さない", "レア", "all"),
    ("3:30絶対蟹に行く", "レア", "jg"),
    ("AA禁止!?", "ウルトラレア", "all"),
    ("1コア　心の鋼","コモン", "all"),
    ("1コア　メジャイ","コモン","all"),
    ("しゃべるとき語尾に「にゃ」をつける、一人称は「ミー」、自分以外は「ユー」","ウルトラレア","all"),
    ("ガンク税を徴収　ガンクごとに１ウェーブ食ってよし","アンコモン","jg"),
    ("1コア目を味方JGに合わせる","レア","lane"),
    ("敵のガンクがわかっていても絶対に下がらない","アンコモン","lane"),
    ("3分に1度ガンクを呼ぶ","アンコモン","lane"),
    ("8分までに3回TOPにロームしてKSする","スーパーレア","sup"),
    ("10分までに4回ガンク","コモン","jg"),
    ("タワー殴るの禁止","コモン","all"),
    ("5分間マウスホイール最大でプレイ","ウルトラレア","all"),
    ("URTを常に反対側に打つ（対象指定の場合対象の体力が多いときにしか使用してはいけない、自身強化の場合は強化中は敵を殴ってはいけない）","レア","all"),
    ("宝箱から進化してはいけない","スーパーレア","sup"),
    ("ワールドアトラス進化後売る","ウルトラレア","sup"),
    ("ASアイテムのみ購入可能","レア","all"),
    ("試合をとおして１５デス","ウルトラレエア","all"),
    ("敵を一人倒すたびに自分も死ぬ","ウルトラレア","all"),
    ("刺せるピンは匿名のみ","コモン","all"),
    ("レーナーに呼ばれるまでずっとファーム","コモン","jg"),
    ("１リコールごとに１ポーション購入","コモン","all"),
    ("1コア　GA購入","コモン","all"),
    ("1コア　ゾーニャの砂時計を購入し溜まるごとに5秒以内に使用","ウルトラレア","all"),
]

# レアリティごとの排出率 (合計100)
RARITY_WEIGHTS = {
    "コモン": 60,
    "アンコモン": 27,
    "レア": 10,
    "スーパーレア": 2.5,
    "ウルトラレア": 0.5,
}

#チャンピオン専用トロール内容
SPECIAL_TROLLS = {
    "サイオン":"パッシブを有効活用する事を言い訳に、試合終了までに10デス以上行う",
    "ノーチラス":"ルーンを覇道、ビルドをフルapにする",
    "ユーミ":"自立しよう！お前は外飼いだ！",
    "ユーミ":"TOP、JG、MID、ADC、TOP….の順番でベストフレンド切り替わるまで乗り換え",
    "アフェリオス":"W禁止",
    "セラフィーン":"絶対に味方に当たらないところでWを使用",
    "スモルダー":"Wだけでスタックを貯める",
    "ブラウム":"「お前さんが盾じゃ！」と言って常に味方を盾にする",
    "アカリ":"絶対に煙幕にだけEを使用する",
    "ヌヌ＆ウィルンプ":"URTを溜めて使用してはいけない",
    "ポッピー":"URTを溜めて使用してはいけない",
    "アイバーン":"Wを常にブッシュに使う",
    "アクシャン":"URTは絶対にチャンピオンに使用してはいけない",
    "アニビア":"壁を使用するときは味方の邪魔をする",
    "アリスター":"WQのコンビを使用してはいけない",
    "アンベッサ":"Q2を敵に当ててはいけない（ミニオンもNG、ブリンクはOK）",
    "ヴィクター":"スキル進化禁止",
    "カイ＝サ":"スキル進化禁止",
    "エイトロックス":"QはQ1のみ使用",
    "ガレン":"体力回復はパッシブorデスのみ（アイテム効果不可）",
    "マルザハール":"征服者選択",
    "キヤナ":"獲得していいエレメントは青のみ",
    "セナ":"落ちてる魂収穫不可",
    "ケイン":"赤・青どちらにもなれる状態じゃないと進化してはいけない",
    "キンドレット":"JGモンスターからのみ印獲得",
    "サイラス":"URTの使用禁止",
    "ザック":"パッシブがあるときは絶対に一度死ぬ",
    "シンジド":"プロキシのみでレーン戦",
    "ジリアン":"スキルはすべて自分に使用",
    "ジン":"4発目使用不可（URTも）",
    "セト":"Wは闘魂ゲージがたまってないときに使用",
    "ティーモ":"3分に一度パッシブを使用して10秒放置",

}

ROLES = ['TOP', 'JG', 'MID', 'ADC', 'SUP']


def get_latest_version():
    """Data Dragonの最新バージョンを取得（失敗時は固定値フォールバック）"""
    try:
        r = requests.get("https://ddragon.leagueoflegends.com/api/versions.json", timeout=5)
        r.raise_for_status()
        return r.json()[0]
    except Exception:
        return "14.17.1"  # 失敗時の保険

def get_champion_data_ja(version):
    """日本語のチャンピオン一覧を取得（id=英語キー, name=日本語名）"""
    url = f"https://ddragon.leagueoflegends.com/cdn/{version}/data/ja_JP/champion.json"
    r = requests.get(url, timeout=6)
    r.raise_for_status()
    return r.json()["data"]  # 例: {"Aatrox": {"id":"Aatrox","name":"エイトロックス",...}, ...}

def index(request):
    if request.method == "POST":
        summoners = [request.POST.get(f"summoner{i}") for i in range(1, 6)]
        troll_count = int(request.POST.get("troll_count", 1))
        request.session["troll_count"] = troll_count
        form = FiveSummonerForm(request.POST)
        if form.is_valid():
            summoners = [form.cleaned_data[f"summoner{i}"] for i in range(1, 6)]
            exclude_yuumi = form.cleaned_data["exclude_yuumi"]
            request.session["summoners"] = summoners
            request.session["exclude_yuumi"] = exclude_yuumi #ユーミの除外をセッションに保存
            return redirect("gacha:result")
    else:
        form = FiveSummonerForm()
    return render(request, "gacha/index.html", {"form": form})

def get_troll(role):
    """ロールに合った候補を返す"""
    role = role.lower()
    if role == "jg":
        candidates = [t for t in TROLLS if t[2] in ("all", "jg")]
    else:
        candidates = [t for t in TROLLS if t[2] in ("all", "lane", role)]
    return candidates


def get_random_troll():
    #レアリティ抽選
    rarities = list(RARITY_WEIGHTS.keys())
    weights = list(RARITY_WEIGHTS.values())
    chosen_rarity = random.choices(rarities, weights=weights, k=1)[0]

    # 選ばれたレアリティから内容をランダムに選ぶ
    candidates = [t for t in TROLLS if t[1] == chosen_rarity]
    content, rarity = random.choice(candidates)
    return content, rarity

def result(request):
    summoners = request.session.get("summoners")
    exclude_yuumi = request.session.get("exclude_yuumi", False)
    troll_count = int(request.session.get("troll_count", 1))  # ← 縛り人数を取得

    if not summoners or len(summoners) != 5:
        return redirect("gacha:index")

    # 最新データ
    version = get_latest_version()
    champ_data = get_champion_data_ja(version)  # dict: key=英語ID, valueに日本語名など
    
    if exclude_yuumi:
        champ_data = {cid: data for cid, data in champ_data.items() if data["name"] != "ユーミ"}

    champ_ids = list(champ_data.keys())

    # サモナーをシャッフル
    shuffled_summoners = random.sample(summoners, k=5)

    # チャンピオンを重複なしで選ぶ
    chosen_champ_ids = random.sample(champ_ids, k=5)

    # --- 縛りを付与する対象をランダムで選ぶ ---
    troll_indices = set(random.sample(range(5), k=troll_count))

    #トロール候補をユニークに確保するし、TROLLSをシャッフルする
    troll_pool = TROLLS[:]
    random.shuffle(troll_pool)

    results = []
    used_trolls = set()
    for i, role in enumerate(ROLES):  # ROLESは固定 ["TOP", "JG", "MID", "ADC", "SUP"]
        champ_id = chosen_champ_ids[i]
        champ_jp = champ_data[champ_id]["name"]
        img_url = f"https://ddragon.leagueoflegends.com/cdn/{version}/img/champion/{champ_id}.png"
        
        if i in troll_indices:
            #トロール抽選
            candidates = get_troll(role)
            candidates = [t for t in candidates if t[0] not in used_trolls]

            # チャンピオン専用のトロールがあれば候補に追加
            if champ_jp in SPECIAL_TROLLS and SPECIAL_TROLLS[champ_jp].strip():
                candidates.append((SPECIAL_TROLLS[champ_jp], "スペシャル", "all"))

            if candidates:
                troll_content, rarity, _ = random.choice(candidates)
                used_trolls.add(troll_content)

            else:
                troll_content = "自由にプレイ"
                rarity = "-"

        else:
            # 縛りなし
            troll_content = "自由にプレイ"
            rarity = "-"

        results.append({
            "role": role,                     
            "summoner": shuffled_summoners[i],
            "champ": champ_jp,
            "champ_img": img_url,
            "troll": troll_content,
            "rarity": rarity,
        })

    return render(request, "gacha/result.html", {"results": results})