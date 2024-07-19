from exam_data_helper import ExamData


def test_s3_helper():
    ######## TESTING s3 filepath method here
    # exam_data = ExamData(source_type='s3', source_value='PATIENT#1165/EXAM#1188')
    # res = exam_data.get_exam_voltage_data()
    # print(res, 'res')

    # # # s3.download_exam_video()
    # res = s3.get_json_keys()
    # print(res, 'res')

    ######## TESTING exam_id method here
    exam_data = ExamData(source_type="exam_id", source_value="1193")
    res = exam_data.get_exam_voltage_data()
    json = exam_data.get_exam_details()
    print(res, "res")
    print(json, "json")
    # exam_data = ExamData(source_type='exam_id', source_value='1188')
    # test = exam_data.download_exam_ambient_noise()
    # print(test, 'test')

    ######## TESTING local method here


if __name__ == "__main__":
    test_s3_helper()
