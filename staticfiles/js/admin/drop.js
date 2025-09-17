document.addEventListener('DOMContentLoaded', function () {
    function toggleDetailInfo(detailInfo) {
        detailInfo.classList.toggle('open');
    }

    function closeOtherDetailInfos(currentDetailInfo) {
        const allDetailInfos = document.querySelectorAll('.detail-info');
        allDetailInfos.forEach(function (detailInfo) {
            if (detailInfo !== currentDetailInfo && detailInfo.classList.contains('open')) {
                detailInfo.scrollTo({ top: 0 });
                detailInfo.classList.remove('open');
            }
        });
    }

    // reusable handler for new and old items
    function documentItemClickHandler() {
        const detailInfo = this.querySelector('.detail-info');
        if (!detailInfo) return;

        detailInfo.scrollTo({ top: 0 });
        toggleDetailInfo(detailInfo);
        closeOtherDetailInfos(detailInfo);
    }

    // Attach to existing .document-item
    const docItems = document.querySelectorAll('.document-item');
    docItems.forEach(doc => {
        doc.addEventListener('click', documentItemClickHandler);
    });

    // Expose handler for getBatchData.js
    window.documentItemClickHandler = documentItemClickHandler;
});
