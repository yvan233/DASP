# 测试类的变量更改后实例的是否会被修改
# 测试结果，会被修改

class Student:              # 类的定义体
    classroom = '101'           # 类变量
    address = 'beijing'

    def __init__(self, name, age):
        self.name = name
        self.age = age

    def print_age(self):
        print('%s: %s' % (self.name, self.age))

li = Student("李四", 24)        
print(li.classroom)
print(Student.classroom)
Student.classroom = "123"

zhang = Student("张三", 23)
print(li.classroom)
print(Student.classroom)
print(zhang.classroom)