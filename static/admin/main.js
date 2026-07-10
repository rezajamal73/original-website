(function () {

    function activateDatepicker($) {

        if (!$.fn.datepicker) {
            console.log("datepicker not loaded");
            return;
        }

        $(".vjDateField").each(function () {

            if ($(this).hasClass("hasDatepicker")) {
                return;
            }

            $(this).datepicker({
                dateFormat: "yy-mm-dd",
                changeMonth: true,
                changeYear: true,
                showOn: "both",
                buttonImageOnly: true,
                isRTL: false,
                buttonText: "یک تاریخ انتخاب کنید",
            });

        });
    }

    $(document).ready(function () {

        if (window.django && window.django.jQuery) {
            activateDatepicker(window.django.jQuery);
        } else if (window.jQuery) {
            activateDatepicker(window.jQuery);
        }

    });

})();