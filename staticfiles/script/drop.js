document.addEventListener('DOMContentLoaded', function() {
    var masterInfos = document.querySelectorAll('.master-info');
    var detailInfos = document.querySelectorAll('.detail-info');
    var doc = document.querySelectorAll('.document-item');

    // masterInfos.forEach(function(masterInfo) {
    //     masterInfo.addEventListener('click', function() {
    //         var detailInfo = this.nextElementSibling;

    //         // Toggle the 'open' class to show/hide the detail info
    //         toggleDetailInfo(detailInfo);

    //         // Close other open detail infos
    //         closeOtherDetailInfos(detailInfo);
    //     });
    // });

    doc.forEach(function(detailInfo) {
        detailInfo.addEventListener('click', function() {
            // console.log("clickek")
            var detailInfo = this.querySelector('.detail-info');

            // Toggle the 'open' class to show/hide the detail info
            toggleDetailInfo(detailInfo);

            // Close other open detail infos
            closeOtherDetailInfos(detailInfo);
        });
    });

    function toggleDetailInfo(detailInfo) {
        detailInfo.classList.toggle('open');
    }

    function closeOtherDetailInfos(currentDetailInfo) {
        var allDetailInfos = document.querySelectorAll('.detail-info');
        allDetailInfos.forEach(function(detailInfo) {
            if (detailInfo !== currentDetailInfo && detailInfo.classList.contains('open')) {
                detailInfo.classList.remove('open');
            }
        });
    }
});



