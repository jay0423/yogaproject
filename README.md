# <div align="center">ヨガ予約アプリ</div>  

###### <div align="center">Djangoで実装したヨガ教室の予約サイトです．</div>  
###### <div align="center">管理者は簡潔にヨガプランを作成できます．</div>
###### <div align="center">高齢者でも見やすく直感的に操作できるUI/UXを実装しました．</div>

<div align="center">
<img src="./img-readme/calendar.PNG" width=600>
</div>

---  

## URL
以下のサイトでご自由に試用できます．（スマホ推奨）  
https://jay-yoga.club/login/  
以下いずれかのIDでログインしてください．  
顧客用の画面： guest  
管理者の画面： admin

## 使用技術・ライブラリ 
- Python 3.6.9
- Django 3.0.5
- PostgreSQL 12.5
- Nginx 1.18.0
- django-pandas 0.6.2
- Pillow 7.1.1

## 画面遷移図
### 顧客用画面

<div align="center">
<img src="./img-readme/画面遷移図_顧客.PNG" width=700>
</div>

### 管理者用画面

<div align="center">
<img src="./img-readme/画面遷移図_管理者.PNG" width=100%>
</div>

## 本アプリの特徴
  
### 顧客側の特徴・メリット
顧客用のIDでログインした場合，顧客用予約画面に遷移します．  
顧客画面の特徴と本アプリを使用するメリットは以下のようになっています．
- 高齢者でも操作しやすいUI/UX（スマホ推奨）
- ログイン後，予約確定までわずか2クリックのみ
- ページが「予約画面」，「予約確認画面」，「アクセス」，「情報」の4つのみ

### 管理者側の画面
管理者用のIDでログインした場合，管理者画面に遷移します．  
管理者側の特徴と本アプリを使用するメリットは以下のようになっています．
- 直観的に操作できるUI/UX
- 曜日ごとにデフォルトプランを作成しておき，予約プランをまとめて作成できる
- ヨガプランを上限なく追加
- 管理者側から予約者の追加やキャンセルが可能
- 登録者情報の閲覧・変更，csvファイルでの出力が可能
- データ分析による売り上げや分析結果の閲覧

## Setup
以下の手順でコマンドコマンドを打ち込むことでローカルで使用いただけます．  
なお，Python3とDjangoを予めインストールされていることを前提とします．  

```bash
python3 -m pip install django-pandas
python3 -m pip install Pillow

git clone https://github.com/jay0423/yogaproject.git

cd yogaproject
python3 manage.py runserver
```

上記の手順で`python3 manage.py runserver`でローカルサーバーを起動した後，http://localhost:8000/login へアクセスし，ID: admin で管理者画面にログインできます．

## アプリの使用方法
使用方法は https://github.com/jay0423/yogaproject/blob/master/static/manual.pdf をご覧ください．
 
  
## Authors
Name: Jumpei Kajimoto  
Email: jay0423@i.softbank.jp
  
