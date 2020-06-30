(function ($) {
    $(function () {

        var selectField1 = $('#id_secret_key');
        var selectField2 = $('#id_exam_paper');
        var selectField3 = $('.deletelink');
        var selectField4 = $('#id_hide_results');
        var save_answers = $('.form-row.field-save_answers');
        var price = $('.form-row.field-price');
        var days = $('.form-row.field-days');
        var save_answers_id = $('#id_save_answers');
        var selectField6 = $('#id_is_paid');

        selectField1.change(function () {
            toggleVerified1($(this).val());
        });
        function toggleVerified1(value) {
            if (value != "") {
                alert("So ! The Quiz will be Locked..okk?? Share the key with right person!!");

            }
        }

       $(document).ready(function () {
            toggleVerified2(selectField2.val());
            checkifpaid(selectField6.val());

        });



        selectField6.change(function () {
            checkifpaid($(this).val());
        });
          function checkifpaid(value) {
            if (value == "True") {
                 price.show();
                days.show();

            } else {
                $('#id_price').val(0);
                price.hide();
                $('#id_days').val(0);
                days.hide();

            }
        }


        selectField2.change(function () {
            toggleVerified2($(this).val());
        });
        function toggleVerified2(value) {
            if (value == "True") {
                save_answers.show();

            } else {
                 save_answers_id.prop('checked', false);
                save_answers.hide();

            }
        }



        selectField3.on('click', function (e) {
            if (selectField4.is(':checked')) {
                e.preventDefault();

                alert("Alert! You have choosen to hide user results , but deleting the quiz will show results to them," +
                    "you can choose to HIDE QUIZ" +"\n"+
                    "Unckeck hide results for deleting this quiz!!!");

            }

        });
    });
})(django.jQuery);
