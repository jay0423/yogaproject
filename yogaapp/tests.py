from django.test import TestCase
from yogaapp.models import BookModel, PlanModel, SettingPlanModel, NoteModel, WeekdayDefaultModel
from django.contrib.auth.models import User
import datetime
 
class ModelTests(TestCase):
    def test_saving_and_retrieving_book_model(self):
        book = BookModel()
        user, plan, time_of_cancel = "ゲスト", "プラン", 1
        book.user = user
        book.plan = plan
        book.time_of_cancel = time_of_cancel
        book.save()

        saved_book = BookModel.objects.all()
        actual_book = saved_book[0]

        self.assertEqual(actual_book.user, user)
        self.assertEqual(actual_book.plan, plan)
        self.assertEqual(actual_book.time_of_cancel, time_of_cancel)
    
    def test_saving_and_retrieving_plan_model(self):
        plan_model = PlanModel()
        s = (datetime.date(2020,1,1), "2020-01", "プラン", "プ", 1, "guest", "ゲスト", "09:00", "スタジオ", 10, 1)
        date, month, plan, short_plan_name, number_of_people, booked_people, booked_people_name, time, location, max_book, plan_num = s
        plan_model.date = date
        plan_model.month = month
        plan_model.plan = plan
        plan_model.short_plan_name = short_plan_name
        plan_model.number_of_people = number_of_people
        plan_model.booked_people = booked_people
        plan_model.booked_people_name = booked_people_name
        plan_model.time = time
        plan_model.location = location
        plan_model.max_book = max_book
        plan_model.plan_num = plan_num
        plan_model.save()

        saved_plan = PlanModel.objects.all()
        actual_plan = saved_plan[0]

        self.assertEqual(actual_plan.date, date)
        self.assertEqual(actual_plan.month, month)
        self.assertEqual(actual_plan.plan, plan)
        self.assertEqual(actual_plan.short_plan_name, short_plan_name)
        self.assertEqual(actual_plan.number_of_people, number_of_people)
        self.assertEqual(actual_plan.booked_people, booked_people)
        self.assertEqual(actual_plan.booked_people_name, booked_people_name)
        self.assertEqual(actual_plan.time, time)
        self.assertEqual(actual_plan.location, location)
        self.assertEqual(actual_plan.max_book, max_book)
        self.assertEqual(actual_plan.plan_num, plan_num)
    
    def test_saving_and_retrieving_setting_plan_model(self):
        plan_model = SettingPlanModel()
        s = ("プラン", "プ", 1000, "スタジオ", 10, "メモ", 1)
        name, short_plan_name, price, location, max_book, memo, plan_num = s
        plan_model.name = name
        plan_model.short_plan_name = short_plan_name
        plan_model.price = price
        plan_model.location = location
        plan_model.max_book = max_book
        plan_model.memo = memo
        plan_model.plan_num = plan_num
        plan_model.save()

        saved_plan = SettingPlanModel.objects.all()
        actual_plan = saved_plan[0]

        self.assertEqual(actual_plan.name, name)
        self.assertEqual(actual_plan.short_plan_name, short_plan_name)
        self.assertEqual(actual_plan.price, price)
        self.assertEqual(actual_plan.location, location)
        self.assertEqual(actual_plan.max_book, max_book)
        self.assertEqual(actual_plan.memo, memo)
        self.assertEqual(actual_plan.plan_num, plan_num)
        
    def test_saving_and_retrieving_note_model(self):
        note = NoteModel()
        memo, num, monday = "メモ", 1, 0
        note.memo = memo
        note.num = num
        note.monday = monday
        note.save()

        saved_note = NoteModel.objects.all()
        actual_note = saved_note[0]

        self.assertEqual(actual_note.memo, memo)
        self.assertEqual(actual_note.num, num)
        self.assertEqual(actual_note.monday, monday)
        
    def test_saving_and_retrieving_weekday_default_model(self):
        weekday_model = WeekdayDefaultModel()
        
        s = ("sunday", "プラン", "09:00", "スタジオ", 10, 1)
        weekday, plan, time, location, max_book, plan_num = s
        weekday_model.weekday = weekday
        weekday_model.plan = plan
        weekday_model.time = time
        weekday_model.location = location
        weekday_model.max_book = max_book
        weekday_model.plan_num = plan_num
        weekday_model.save()

        saved_weekday = WeekdayDefaultModel.objects.all()
        actual_weekday = saved_weekday[0]

        self.assertEqual(actual_weekday.weekday, weekday)
        self.assertEqual(actual_weekday.plan, plan)
        self.assertEqual(actual_weekday.time, time)
        self.assertEqual(actual_weekday.location, location)
        self.assertEqual(actual_weekday.max_book, max_book)
        self.assertEqual(actual_weekday.plan_num, plan_num)
        
        
class ViewTests(TestCase):
    def setUp(self):
        user = User.objects.create_user(username="test", password="password", email="test@test.com", is_active=True, first_name="太郎", last_name="テスト")
        user.save()
        #BookModelへのユーザーの登録
        user_plan = BookModel.objects.create(user="test")
        user_plan.save()
        #NoteModelへの登録
        note = NoteModel.objects.create(memo="", num=0, monday=0)
        note.save()

    def test_index(self):
        client = self.client

        #ログイン可否の確認
        urls = ['/book/0/confirm/2020-01-01/', '/booked_list', '/access', '/info', '/book/0', '/book_admin/0', '/users', '/users/update/test', '/analysis/', '/table/', '/setting_plan/', '/create/', '/note/', '/calendar_default/']
        for u in urls:
            response = client.get(u) # まずはログインしていないユーザがアクセスした場合
            self.assertEqual(response.status_code, 302) # ステータスコード：302が返却され画面にアクセスできない
            client.login(username='test', password='password') # setUpで追加しておいたユーザでログインします
            response = client.get(u) # ログインしているユーザがアクセスした場合
            self.assertEqual(response.status_code, 200) # ステータスコード：200が返却され画面にアクセスできている
            client.logout() #ログアウトする．