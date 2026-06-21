document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    const browseBtn = document.getElementById('browseBtn');
    const uploadCard = document.getElementById('uploadCard');
    const cameraCard = document.getElementById('cameraCard');
    const calibrationCard = document.getElementById('calibrationCard');
    const previewCard = document.getElementById('previewCard');
    const annotatedImage = document.getElementById('annotatedImage');
    const loadingOverlay = document.getElementById('loadingOverlay');
    const reuploadBtn = document.getElementById('reuploadBtn');
    const scanBtn = document.getElementById('scanBtn');
    
    // Camera elements
    const cameraVideo = document.getElementById('cameraVideo');
    const cameraCanvas = document.getElementById('cameraCanvas');
    const overlayCanvas = document.getElementById('overlayCanvas');
    const cameraGuideOverlay = document.getElementById('cameraGuideOverlay');
    const startCameraBtn = document.getElementById('startCameraBtn');
    const captureBtn = document.getElementById('captureBtn');
    const stopCameraBtn = document.getElementById('stopCameraBtn');
    
    // Calibration sliders
    const rangeExpand = document.getElementById('rangeExpand');
    const rangeMoveLR = document.getElementById('rangeMoveLR');
    const rangeMoveUD = document.getElementById('rangeMoveUD');
    
    // Mode tabs
    const modeTabs = document.querySelectorAll('.mode-tab');
    
    // Results & Invoice elements
    const dishesListContainer = document.getElementById('dishesListContainer');
    const detectedCount = document.getElementById('detectedCount');
    const invoiceItemsContainer = document.getElementById('invoiceItemsContainer');
    const billSubtotal = document.getElementById('billSubtotal');
    const billTotal = document.getElementById('billTotal');
    const invoiceDate = document.getElementById('invoiceDate');
    const invoiceTime = document.getElementById('invoiceTime');
    const headerStatus = document.getElementById('headerStatus');
    const statusIndicator = headerStatus.querySelector('.status-indicator');
    const statusText = headerStatus.querySelector('.status-text');
    const resetBtn = document.getElementById('resetBtn');
    const printBtn = document.getElementById('printBtn');
    
    // State
    let currentImageFile = null;
    let mediaStream = null;
    let currentMode = 'upload';
    let animationId = null;
    let isProcessing = false;
    
    // Format currency
    function formatCurrency(value) {
        return value.toLocaleString('vi-VN') + ' VNĐ';
    }
    
    // Gửi ảnh lên server với tham số cắt hiện tại
    async function sendImageToServer(imageFile, expand, moveLR, moveUD) {
        if (isProcessing) return;
        isProcessing = true;
        
        statusIndicator.className = 'status-indicator loading';
        statusText.textContent = 'Đang nhận diện món ăn...';
        loadingOverlay.classList.add('active');
        
        const formData = new FormData();
        formData.append('image', imageFile);
        formData.append('expand', expand);
        formData.append('move_lr', moveLR);
        formData.append('move_ud', moveUD);
        
        try {
            const response = await fetch('/api/detect', { method: 'POST', body: formData });
            if (!response.ok) throw new Error('Server error');
            const data = await response.json();
            
            statusIndicator.className = 'status-indicator success';
            statusText.textContent = 'Nhận diện hoàn tất!';
            loadingOverlay.classList.remove('active');
            
            annotatedImage.src = data.annotated_image;
            resetBtn.disabled = false;
            printBtn.disabled = false;
            
            renderResults(data.items);
            renderInvoice(data.items, data.total_price);
        } catch (err) {
            console.error(err);
            statusIndicator.className = 'status-indicator idle';
            statusText.textContent = 'Lỗi nhận diện!';
            loadingOverlay.classList.remove('active');
            alert('Có lỗi xảy ra: ' + err.message);
        } finally {
            isProcessing = false;
        }
    }
    
    // Chỉ hiển thị khung trên ảnh (không gửi request)
    async function updateFrameOnly(imageFile, expand, moveLR, moveUD) {
        if (!imageFile) return;
        
        const formData = new FormData();
        formData.append('image', imageFile);
        formData.append('expand', expand);
        formData.append('move_lr', moveLR);
        formData.append('move_ud', moveUD);
        
        try {
            const response = await fetch('/api/detect', { method: 'POST', body: formData });
            if (!response.ok) throw new Error('Server error');
            const data = await response.json();
            annotatedImage.src = data.annotated_image;
        } catch (err) {
            console.error('Error updating frame:', err);
        }
    }
    
    // Render results
    function renderResults(items) {
        dishesListContainer.innerHTML = '';
        detectedCount.textContent = `${items.length} món`;
        const listWrapper = document.createElement('div');
        listWrapper.className = 'dishes-list';
        
        items.forEach(item => {
            const confPercent = item.confidence_percent || Math.round(item.confidence * 100);
            let eggBadge = '';
            if (item.egg_count && item.egg_count > 0) {
                eggBadge = `<span class="egg-badge"><i class="fa-solid fa-egg"></i> ${item.egg_count} trứng</span>`;
            }
            const isConfident = item.is_confident !== false;
            const warnIcon = !isConfident ? '<i class="fa-solid fa-triangle-exclamation" style="color: #f39c12; margin-right: 5px;"></i>' : '';
            
            listWrapper.innerHTML += `
                <div class="dish-item ${!isConfident ? 'low-confidence' : ''}">
                    <div class="dish-thumbnail"><img src="${item.crop_image}" alt=""></div>
                    <div class="dish-details">
                        <span class="dish-region">${item.region_name}</span>
                        <h3 class="dish-name">${warnIcon}${item.dish_name}</h3>
                        <div class="dish-extra">
                            ${eggBadge}
                            <div class="confidence-bar-container">
                                <div class="confidence-bar"><div class="confidence-fill" style="width: ${confPercent}%; background: ${isConfident ? '#2ecc71' : '#f39c12'}"></div></div>
                                <span class="confidence-text">${confPercent}%</span>
                            </div>
                        </div>
                    </div>
                    <div class="dish-price">${formatCurrency(item.price)}</div>
                </div>
            `;
        });
        dishesListContainer.appendChild(listWrapper);
    }
    
    function renderInvoice(items, totalPrice) {
        invoiceItemsContainer.innerHTML = '';
        const now = new Date();
        invoiceDate.textContent = `Ngày: ${now.toLocaleDateString('vi-VN')}`;
        invoiceTime.textContent = `Giờ: ${now.toLocaleTimeString('vi-VN')}`;
        
        if (items.length === 0) {
            invoiceItemsContainer.innerHTML = `<p class="empty-invoice-text">Hóa đơn trống</p>`;
        } else {
            items.forEach(item => {
                const subDetail = (item.egg_count && item.egg_count > 0) ? `(${item.egg_count} quả trứng)` : '';
                invoiceItemsContainer.innerHTML += `
                    <div class="invoice-item-row">
                        <div class="invoice-item-left">
                            <span class="invoice-item-name">${item.dish_name}</span>
                            <span class="invoice-item-sub">${item.region_name} ${subDetail}</span>
                        </div>
                        <div class="invoice-item-price">${formatCurrency(item.price)}</div>
                    </div>
                `;
            });
        }
        billSubtotal.textContent = formatCurrency(totalPrice);
        billTotal.textContent = formatCurrency(totalPrice);
    }
    
    // ==================== CAMERA FUNCTIONS ====================
    const cropRegions = {
        o_tren_trai: { x1: 21.5, y1: 9.5, x2: 41.5, y2: 41.5 },
        o_tren_giua: { x1: 42.0, y1: 10.5, x2: 61.5, y2: 42.5 },
        o_tren_phai: { x1: 61.5, y1: 11.5, x2: 81.5, y2: 44.5 },
        o_duoi_trai: { x1: 19.5, y1: 43.0, x2: 44.5, y2: 91.5 },
        o_duoi_phai: { x1: 50.0, y1: 45.0, x2: 80.5, y2: 93.5 }
    };
    
    const regionNames = {
        o_tren_trai: 'Trên trái', o_tren_giua: 'Trên giữa', o_tren_phai: 'Trên phải',
        o_duoi_trai: 'Dưới trái', o_duoi_phai: 'Dưới phải'
    };
    
    function drawOverlay() {
        if (!overlayCanvas || !cameraVideo.videoWidth) return;
        
        const expand = parseInt(rangeExpand.value) || 0;
        const moveLR = parseInt(rangeMoveLR.value) || 0;
        const moveUD = parseInt(rangeMoveUD.value) || 0;
        
        const width = cameraVideo.clientWidth;
        const height = cameraVideo.clientHeight;
        
        overlayCanvas.width = width;
        overlayCanvas.height = height;
        
        const ctx = overlayCanvas.getContext('2d');
        ctx.clearRect(0, 0, width, height);
        
        for (const [key, region] of Object.entries(cropRegions)) {
            let x1 = (region.x1 + moveLR/10) * width / 100 - expand;
            let y1 = (region.y1 + moveUD/10) * height / 100 - expand;
            let x2 = (region.x2 + moveLR/10) * width / 100 + expand;
            let y2 = (region.y2 + moveUD/10) * height / 100 + expand;
            
            x1 = Math.max(0, x1);
            y1 = Math.max(0, y1);
            x2 = Math.min(width, x2);
            y2 = Math.min(height, y2);
            
            ctx.strokeStyle = '#2ecc71';
            ctx.lineWidth = 3;
            ctx.strokeRect(x1, y1, x2 - x1, y2 - y1);
            
            ctx.fillStyle = 'rgba(46, 204, 113, 0.15)';
            ctx.fillRect(x1, y1, x2 - x1, y2 - y1);
            
            ctx.fillStyle = '#2ecc71';
            ctx.font = 'bold 14px "Inter"';
            ctx.fillText(regionNames[key], x1 + 5, y1 + 25);
        }
    }
    
    function updateOverlay() {
        if (currentMode === 'camera' && cameraVideo.videoWidth) {
            drawOverlay();
        }
    }
    
    async function captureFromCamera() {
        if (!cameraVideo.videoWidth || !cameraVideo.videoHeight) {
            alert('Camera chưa sẵn sàng! Hãy mở camera trước.');
            return null;
        }
        
        const expand = parseInt(rangeExpand.value) || 0;
        const moveLR = parseInt(rangeMoveLR.value) || 0;
        const moveUD = parseInt(rangeMoveUD.value) || 0;
        
        const videoWidth = cameraVideo.videoWidth;
        const videoHeight = cameraVideo.videoHeight;
        
        // Tạo canvas tạm để vẽ ảnh từ camera (đã mirror)
        const tempCanvas = document.createElement('canvas');
        tempCanvas.width = videoWidth;
        tempCanvas.height = videoHeight;
        const tempCtx = tempCanvas.getContext('2d');
        tempCtx.save();
        tempCtx.scale(-1, 1);
        tempCtx.drawImage(cameraVideo, -videoWidth, 0, videoWidth, videoHeight);
        tempCtx.restore();
        
        // Tạo canvas kết quả
        const resultCanvas = document.createElement('canvas');
        resultCanvas.width = 1000;
        resultCanvas.height = 1000;
        const resultCtx = resultCanvas.getContext('2d');
        
        // Vị trí các ô trên ảnh kết quả
        const positions = [
            { name: 'o_tren_trai', x: 0, y: 0, width: 200, height: 320 },
            { name: 'o_tren_giua', x: 205, y: 0, width: 195, height: 320 },
            { name: 'o_tren_phai', x: 405, y: 0, width: 200, height: 330 },
            { name: 'o_duoi_trai', x: 0, y: 325, width: 250, height: 485 },
            { name: 'o_duoi_phai', x: 255, y: 325, width: 305, height: 485 }
        ];
        
        for (const pos of positions) {
            const region = cropRegions[pos.name];
            let x1 = (region.x1 + moveLR/10) * videoWidth / 100 - expand;
            let y1 = (region.y1 + moveUD/10) * videoHeight / 100 - expand;
            let x2 = (region.x2 + moveLR/10) * videoWidth / 100 + expand;
            let y2 = (region.y2 + moveUD/10) * videoHeight / 100 + expand;
            
            x1 = Math.max(0, x1);
            y1 = Math.max(0, y1);
            x2 = Math.min(videoWidth, x2);
            y2 = Math.min(videoHeight, y2);
            
            if (x2 > x1 && y2 > y1) {
                const tempCropCanvas = document.createElement('canvas');
                tempCropCanvas.width = pos.width;
                tempCropCanvas.height = pos.height;
                const tempCropCtx = tempCropCanvas.getContext('2d');
                tempCropCtx.drawImage(
                    tempCanvas, x1, y1, x2 - x1, y2 - y1, 0, 0, pos.width, pos.height
                );
                resultCtx.drawImage(tempCropCanvas, pos.x, pos.y);
            }
        }
        
        return new Promise((resolve) => {
            resultCanvas.toBlob(blob => {
                const file = new File([blob], 'camera_capture.jpg', { type: 'image/jpeg' });
                resolve(file);
            }, 'image/jpeg', 0.95);
        });
    }
    
    async function startCamera() {
        try {
            if (mediaStream) stopCamera();
            mediaStream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' } });
            cameraVideo.srcObject = mediaStream;
            
            cameraVideo.onloadedmetadata = () => {
                cameraVideo.play();
                startCameraBtn.disabled = true;
                captureBtn.disabled = false;
                stopCameraBtn.disabled = false;
                cameraGuideOverlay.classList.add('hidden');
                
                if (animationId) cancelAnimationFrame(animationId);
                function drawLoop() {
                    drawOverlay();
                    animationId = requestAnimationFrame(drawLoop);
                }
                drawLoop();
            };
            statusText.textContent = 'Camera đã sẵn sàng';
        } catch (err) {
            console.error(err);
            alert('Không thể mở camera. Vui lòng kiểm tra quyền truy cập.');
            statusText.textContent = 'Lỗi camera!';
        }
    }
    
    function stopCamera() {
        if (mediaStream) {
            mediaStream.getTracks().forEach(track => track.stop());
            mediaStream = null;
        }
        cameraVideo.srcObject = null;
        if (animationId) cancelAnimationFrame(animationId);
        
        startCameraBtn.disabled = false;
        captureBtn.disabled = true;
        stopCameraBtn.disabled = true;
        cameraGuideOverlay.classList.remove('hidden');
        statusText.textContent = 'Camera đã tắt';
        
        const ctx = overlayCanvas.getContext('2d');
        if (ctx) ctx.clearRect(0, 0, overlayCanvas.width, overlayCanvas.height);
    }
    
    async function doCaptureAndDetect() {
        const file = await captureFromCamera();
        if (file) {
            currentImageFile = file;
            uploadCard.style.display = 'none';
            cameraCard.style.display = 'none';
            previewCard.style.display = 'block';
            calibrationCard.style.display = 'block';
            await sendImageToServer(file, rangeExpand.value, rangeMoveLR.value, rangeMoveUD.value);
            stopCamera();
        }
    }
    
    async function doScan() {
        if (currentMode === 'camera') {
            // Chụp từ camera
            await doCaptureAndDetect();
        } else if (currentImageFile) {
            // Upload đã có ảnh
            await sendImageToServer(currentImageFile, rangeExpand.value, rangeMoveLR.value, rangeMoveUD.value);
        } else {
            alert('Vui lòng chọn ảnh hoặc mở camera trước!');
        }
    }
    
    // ==================== UPLOAD FUNCTIONS ====================
    function handleImageFile(file) {
        if (!file.type.startsWith('image/')) {
            alert('Vui lòng chọn file ảnh hợp lệ!');
            return;
        }
        currentImageFile = file;
        
        uploadCard.style.display = 'none';
        cameraCard.style.display = 'none';
        previewCard.style.display = 'block';
        calibrationCard.style.display = 'block';
        
        const reader = new FileReader();
        reader.onload = (e) => {
            annotatedImage.src = e.target.result;
            updateFrameOnly(file, rangeExpand.value, rangeMoveLR.value, rangeMoveUD.value);
        };
        reader.readAsDataURL(file);
    }
    
    // ==================== RESET FUNCTION ====================
    function resetApp() {
        stopCamera();
        currentImageFile = null;
        fileInput.value = '';
        
        rangeExpand.value = 0;
        rangeMoveLR.value = 0;
        rangeMoveUD.value = 0;
        
        uploadCard.style.display = currentMode === 'upload' ? 'block' : 'none';
        cameraCard.style.display = currentMode === 'camera' ? 'block' : 'none';
        calibrationCard.style.display = 'none';
        previewCard.style.display = 'none';
        annotatedImage.src = '';
        
        dishesListContainer.innerHTML = `<div class="empty-state"><i class="fa-solid fa-circle-info"></i><p>Tải ảnh hoặc chụp ảnh khay cơm để hiển thị danh sách món ăn</p></div>`;
        detectedCount.textContent = '0 món';
        invoiceItemsContainer.innerHTML = `<p class="empty-invoice-text">Hóa đơn trống</p>`;
        billSubtotal.textContent = '0 VNĐ';
        billTotal.textContent = '0 VNĐ';
        invoiceDate.textContent = 'Ngày: --/--/----';
        invoiceTime.textContent = 'Giờ: --:--:--';
        resetBtn.disabled = true;
        printBtn.disabled = true;
        statusIndicator.className = 'status-indicator idle';
        statusText.textContent = 'Đang chờ hình ảnh...';
    }
    
    // ==================== MODE SWITCHING ====================
    function switchMode(mode) {
        currentMode = mode;
        modeTabs.forEach(tab => {
            tab.classList.toggle('active', tab.dataset.mode === mode);
        });
        
        if (mode === 'upload') {
            stopCamera();
            uploadCard.style.display = 'block';
            cameraCard.style.display = 'none';
        } else {
            uploadCard.style.display = 'none';
            cameraCard.style.display = 'block';
            // Tự động mở camera khi chuyển sang chế độ camera
            startCamera();
        }
        calibrationCard.style.display = 'none';
        previewCard.style.display = 'none';
        currentImageFile = null;
    }
    
    // ==================== EVENT LISTENERS ====================
    // Upload handlers
    browseBtn.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length) {
            switchMode('upload');
            handleImageFile(e.target.files[0]);
        }
    });
    
    dropZone.addEventListener('dragover', (e) => { e.preventDefault(); dropZone.classList.add('drag-over'); });
    dropZone.addEventListener('dragleave', () => dropZone.classList.remove('drag-over'));
    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('drag-over');
        if (e.dataTransfer.files.length) {
            switchMode('upload');
            handleImageFile(e.dataTransfer.files[0]);
        }
    });
    
    // Slider events - chỉ cập nhật khung
    rangeExpand.addEventListener('input', () => {
        if (currentMode === 'camera') {
            updateOverlay();
        } else if (currentImageFile) {
            updateFrameOnly(currentImageFile, rangeExpand.value, rangeMoveLR.value, rangeMoveUD.value);
        }
    });
    rangeMoveLR.addEventListener('input', () => {
        if (currentMode === 'camera') {
            updateOverlay();
        } else if (currentImageFile) {
            updateFrameOnly(currentImageFile, rangeExpand.value, rangeMoveLR.value, rangeMoveUD.value);
        }
    });
    rangeMoveUD.addEventListener('input', () => {
        if (currentMode === 'camera') {
            updateOverlay();
        } else if (currentImageFile) {
            updateFrameOnly(currentImageFile, rangeExpand.value, rangeMoveLR.value, rangeMoveUD.value);
        }
    });
    
    // SCAN button
    scanBtn.addEventListener('click', doScan);
    
    // Camera handlers
    startCameraBtn.addEventListener('click', startCamera);
    stopCameraBtn.addEventListener('click', stopCamera);
    captureBtn.addEventListener('click', doCaptureAndDetect);
    
    window.addEventListener('resize', () => updateOverlay());
    
    // Mode tabs
    modeTabs.forEach(tab => {
        tab.addEventListener('click', () => switchMode(tab.dataset.mode));
    });
    
    // Reset and reupload
    reuploadBtn.addEventListener('click', resetApp);
    resetBtn.addEventListener('click', resetApp);
    printBtn.addEventListener('click', () => window.print());
    
    resetApp();
});