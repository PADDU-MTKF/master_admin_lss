document.addEventListener('DOMContentLoaded', function () {
    let offset = document.querySelectorAll('.document-list .document-item').length;

    let isLoading = false;
    let allFetched = false;

    const dbId = document.querySelector("input[name='db_id']").value;
    const collectionId = document.querySelector("input[name='collection_id']").value;

    const list = document.querySelector('.document-list'); // corrected selector
    const loading = document.getElementById('loading');
    const allFetchedMsg = document.getElementById('all-fetched');
    const loadMoreBtn = document.getElementById('load-more-btn');

    async function loadMore() {
        if (isLoading || allFetched) return;
        isLoading = true;
        loading.style.display = 'block';

        try {
            const response = await fetch(
                `/admin/get-documents-batch/?offset=${offset}&db_id=${dbId}&collection_id=${collectionId}`
            );
            const data = await response.json();
            const docs = data.data;
            const sessionExp=data.sessionExp;

            // 🔹 If session expired, redirect immediately
            if (sessionExp) {
                window.location.href = "/admin";
                return;
            }

            if (docs.length === 0) {
                allFetched = true;
                loading.style.display = 'none';
                loadMoreBtn.style.display = 'none';
                allFetchedMsg.style.display = 'block';
                setTimeout(() => {
                    allFetchedMsg.style.display = 'none';
                }, 3000);
                return;
            }

            docs.forEach((doc, index) => {
                // Create the wrapper
                const wrapper = document.createElement('div');
                wrapper.classList.add('document-item');

                // Master info (slno)
                const masterInfo = document.createElement('div');
                masterInfo.classList.add('master-info');
                const slno = document.createElement('span');
                slno.classList.add('slno');
                slno.textContent = offset + index + 1; // continue numbering
                masterInfo.appendChild(slno);

                // Detail info
                const detailInfo = document.createElement('div');
                detailInfo.classList.add('detail-info');

                Object.entries(doc).forEach(([title, value]) => {
                    if (title !== "id") {
                        const flexDiv = document.createElement('div');
                        flexDiv.classList.add('flex');
                        if (title.includes("Image") && value) {
                            flexDiv.classList.add('col');
                        }

                        const capDiv = document.createElement('div');
                        capDiv.classList.add('cap');
                        capDiv.textContent = title;

                        const valDiv = document.createElement('div');
                        valDiv.classList.add('value');

                        if (title.includes("Image") && value) {
                            const img = document.createElement('img');
                            img.src = value;
                            img.alt = title;
                            img.classList.add('small-round-img');
                            valDiv.appendChild(img);

                            const hiddenImg = document.createElement('input');
                            hiddenImg.type = 'hidden';
                            hiddenImg.name = `img_${doc.id}[]`;
                            hiddenImg.value = value;
                            valDiv.appendChild(hiddenImg);
                        } else {
                            valDiv.textContent = `: ${value}`;
                        }

                        flexDiv.appendChild(capDiv);
                        flexDiv.appendChild(valDiv);
                        detailInfo.appendChild(flexDiv);
                    }
                });

                // Edit/Delete buttons
                const actionDiv = document.createElement('div');

                const hiddenData = document.createElement('input');
                hiddenData.type = 'hidden';
                hiddenData.name = `data_${doc.id}`;
                hiddenData.value = JSON.stringify(doc);
                actionDiv.appendChild(hiddenData);

                const editBtn = document.createElement('button');
                editBtn.classList.add('btn-ed');
                editBtn.type = 'submit';
                editBtn.name = 'edit';
                editBtn.value = doc.id;
                editBtn.textContent = 'Edit';
                actionDiv.appendChild(editBtn);

                const deleteBtn = document.createElement('button');
                deleteBtn.classList.add('btn-ed');
                deleteBtn.type = 'submit';
                deleteBtn.name = 'delete';
                deleteBtn.value = doc.id;
                deleteBtn.textContent = 'Delete';
                deleteBtn.onclick = () => confirmDelete();
                actionDiv.appendChild(deleteBtn);

                detailInfo.appendChild(actionDiv);

                // Append all together
                wrapper.appendChild(masterInfo);
                wrapper.appendChild(detailInfo);
                list.appendChild(wrapper);

                // Attach event only to this new element
                if (window.documentItemClickHandler) {
                    wrapper.addEventListener('click', window.documentItemClickHandler);
                }
            });

            offset += docs.length;
        } catch (err) {
            console.error("Error loading more docs:", err);
        } finally {
            loading.style.display = 'none';
            isLoading = false;
        }
    }

    // Load more button click
    loadMoreBtn.addEventListener('click', loadMore);
});
