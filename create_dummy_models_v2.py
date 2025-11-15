import os

# هذا الملف يقوم بإنشاء مجلدات نماذج فارغة
# لتسهيل تشغيل التطبيق في حالة عدم وجود النماذج المدربة
# هذا يساعد في اختبار أن التطبيق يعمل بشكل صحيح

# قائمة بأسماء المجلدات التي ستمثل النماذج
models_to_create = [
    'BrainTumor10EpochsCategorical.h5',
    'SkinCancerModel.h5',
    'EyeDiseaseModel.h5'
]

# هيكل المجلدات الوهمي
dummy_model_structure = {
    'assets': {},
    'variables': {
        'variables.data-00000-of-00001': '',
        'variables.index': ''
    },
    'keras_metadata.pb': '',
    'saved_model.pb': ''
}

def create_dummy_directory_structure(path, structure):
    for name, content in structure.items():
        current_path = os.path.join(path, name)
        if isinstance(content, dict):
            os.makedirs(current_path, exist_ok=True)
            create_dummy_directory_structure(current_path, content)
        else:
            with open(current_path, 'w') as f:
                f.write('')

for model_name in models_to_create:
    if not os.path.exists(model_name):
        os.makedirs(model_name)
        create_dummy_directory_structure(model_name, dummy_model_structure)
        print(f"تم إنشاء مجلد النموذج الوهمي '{model_name}' بنجاح.")
    else:
        print(f"المجلد '{model_name}' موجود بالفعل. تخطي الإنشاء.")

print("\nتم الانتهاء من إنشاء جميع مجلدات النماذج الوهمية.")
print("الآن يمكنك تشغيل ملف 'app.py' لاختبار التطبيق.")
