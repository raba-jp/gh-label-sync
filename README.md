# github-label-sync
Github自動ラベル設定スクリプト

## Instration
```
pip install git+https://github.com/vivitInc/github-label-sync.git
```

## Usage
```
# config.yaml
namespace: XXX # Githubのユーザ名またはオーガニゼーション名
is_user: false # `namespace`がユーザ名の場合、 `true` にする

# ユーザ、オーガニゼーションを横断して設定したい場合
# ネームスペース/リポジトリ名の形式で記述する
repositories:
  - vivitInc/github-label-sync

# 設定したいラベルの名前、色、説明を記述する
labels:
  - name: XXX
    color: FFFFFF
    description: XXX
```

### namespace全体に対してラベルを設定する
```
github-label-sync sync
```

### 設定ファイルに記述したリポジトリのみラベルを設定する
```
github-label-sync sync --mode=list
```

### 使用する設定ファイルを指定する
```
github-label-sync sync filepath=config.yaml
```

## for Developer
```
pipenv install
pipenv shell
```
