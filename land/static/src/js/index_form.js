document.addEventListener('DOMContentLoaded', function () {
    const vatInput = document.getElementById('vat');
    const tIdentiInput = document.getElementById('tipo_identificacion');
    let debounceTimer = null;

    // ===== Input de adjunto: mostrar múltiples archivos cargados =====
    const adjuntoInput = document.getElementById('adjunto');
    const fileUploadZone = document.getElementById('file_upload_zone');
    const filePreview = document.getElementById('file_preview');
    const fileList = document.getElementById('file_list');
    const uploadText = document.getElementById('upload_text');
    const uploadIcon = document.querySelector('.upload-icon');

    // Función para formatear el tamaño del archivo
    function formatFileSize(bytes) {
        if (bytes < 1024) return bytes + ' B';
        if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
        return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
    }

    adjuntoInput.addEventListener('change', function () {
        const files = this.files;

        if (files && files.length > 0) {
            // Agregar clase para cambiar el estilo de la zona
            fileUploadZone.classList.add('has-file');

            // Ocultar el texto e ícono de subida
            uploadText.style.display = 'none';
            if (uploadIcon) uploadIcon.style.display = 'none';

            // Mostrar la zona de previsualización
            filePreview.style.display = 'block';
            fileList.innerHTML = ''; // Limpiar lista anterior

            // Recorrer todos los archivos seleccionados
            for (let i = 0; i < files.length; i++) {
                const file = files[i];

                // Crear contenedor para cada archivo
                const fileItem = document.createElement('div');
                fileItem.className = 'file-item';
                fileItem.style.cssText = `
                    display: flex;
                    align-items: center;
                    gap: 12px;
                    margin-bottom: 8px;
                    padding: 8px 12px;
                    border: 1px solid #e0e0e0;
                    border-radius: 8px;
                    background: #f9f9f9;
                    transition: background 0.2s;
                `;

                // Verificar si es imagen para mostrar preview
                if (file.type && file.type.startsWith('image/')) {
                    const reader = new FileReader();
                    reader.onload = function (e) {
                        const img = document.createElement('img');
                        img.src = e.target.result;
                        img.alt = file.name;
                        img.style.cssText = `
                            width: 50px;
                            height: 50px;
                            object-fit: cover;
                            border-radius: 6px;
                            border: 1px solid #ddd;
                            flex-shrink: 0;
                        `;
                        fileItem.insertBefore(img, fileItem.firstChild);
                    };
                    reader.readAsDataURL(file);
                } else {
                    // Icono para archivos que no son imagen
                    const iconSpan = document.createElement('span');
                    iconSpan.textContent = '📄';
                    iconSpan.style.cssText = 'font-size: 30px; flex-shrink: 0;';
                    fileItem.appendChild(iconSpan);
                }

                // Nombre del archivo
                const nameSpan = document.createElement('span');
                nameSpan.textContent = file.name;
                nameSpan.style.cssText = `
                    font-size: 14px;
                    font-weight: 500;
                    color: #333;
                    word-break: break-all;
                    flex: 1;
                `;

                // Tamaño del archivo
                const sizeSpan = document.createElement('span');
                sizeSpan.textContent = formatFileSize(file.size);
                sizeSpan.style.cssText = `
                    font-size: 12px;
                    color: #999;
                    flex-shrink: 0;
                `;

                // Botón para eliminar archivo individual (opcional)
                const removeBtn = document.createElement('button');
                removeBtn.textContent = '✕';
                removeBtn.type = 'button';
                removeBtn.style.cssText = `
                    background: none;
                    border: none;
                    color: #dc3545;
                    font-size: 18px;
                    cursor: pointer;
                    padding: 0 4px;
                    flex-shrink: 0;
                `;
                removeBtn.title = 'Eliminar este archivo';
                removeBtn.addEventListener('click', function (e) {
                    e.stopPropagation();
                    // Eliminar este archivo de la lista
                    const dt = new DataTransfer();
                    const currentFiles = adjuntoInput.files;
                    for (let j = 0; j < currentFiles.length; j++) {
                        if (j !== i) {
                            dt.items.add(currentFiles[j]);
                        }
                    }
                    adjuntoInput.files = dt.files;
                    // Disparar evento change para actualizar la vista
                    adjuntoInput.dispatchEvent(new Event('change', { bubbles: true }));
                });

                fileItem.appendChild(nameSpan);
                fileItem.appendChild(sizeSpan);
                fileItem.appendChild(removeBtn);
                fileList.appendChild(fileItem);
            }

            // Actualizar texto del contador de archivos
            const fileCount = files.length;
            const countSpan = document.createElement('span');
            countSpan.style.cssText = `
                display: block;
                font-size: 14px;
                color: #667eea;
                font-weight: 600;
                margin-top: 8px;
                text-align: center;
            `;
            countSpan.textContent = `📎 ${fileCount} archivo${fileCount > 1 ? 's' : ''} seleccionado${fileCount > 1 ? 's' : ''}`;

            // Verificar si ya existe un contador y reemplazarlo
            const existingCount = fileList.querySelector('.file-count');
            if (existingCount) {
                existingCount.textContent = countSpan.textContent;
            } else {
                countSpan.className = 'file-count';
                fileList.appendChild(countSpan);
            }

        } else {
            // No hay archivos seleccionados -> estado inicial
            fileUploadZone.classList.remove('has-file');
            filePreview.style.display = 'none';
            fileList.innerHTML = '';
            uploadText.style.display = 'block';
            if (uploadIcon) uploadIcon.style.display = 'block';
        }
    });

    // ===== Soporte para arrastrar y soltar múltiples archivos =====
    fileUploadZone.addEventListener('dragover', function (e) {
        e.preventDefault();
        this.style.borderColor = '#667eea';
        this.style.background = '#f5f7ff';
    });

    fileUploadZone.addEventListener('dragleave', function (e) {
        e.preventDefault();
        this.style.borderColor = '#c0c0c0';
        this.style.background = '#fafafa';
    });

    fileUploadZone.addEventListener('drop', function (e) {
        e.preventDefault();
        this.style.borderColor = '#c0c0c0';
        this.style.background = '#fafafa';

        const files = e.dataTransfer.files;
        if (files.length > 0) {
            adjuntoInput.files = files;
            // Disparar el evento change para actualizar la vista previa
            adjuntoInput.dispatchEvent(new Event('change', { bubbles: true }));
        }
    });

    // ===== El resto de tu código (consultarCliente, lotes, etc.) se mantiene igual =====
    // ... (mantén todo el código existente de consultarCliente, eventos, etc.)

    function consultarCliente() {
        const vat = vatInput.value.trim();
        if (!vat) {
            return;
        }

        fetch('/api/land/client/' + encodeURIComponent(vat), {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                jsonrpc: '2.0',
                method: 'call',
                params: {
                   'code':  tIdentiInput.value.trim()
                }
            })
        })
        .then(function (response) {
            return response.json();
        })
        .then(function (data) {
            var result = data;
            if (data && data.hasOwnProperty('result')) {
                result = data.result;
            }
            if (result && result.success) {
                document.getElementById('nombres_apellidos').value = result.name || '';
                document.getElementById('celular').placeholder = result.phone || '';
                document.getElementById('correo').placeholder = result.email || '';
                if (result.type_identification) {
                  document.getElementById('tipo_identificacion').value = result.type_identification || '';
                }

                var lotesContainer = document.getElementById('lotes_container');
                var lotesGroup = document.getElementById('lotes_group');
                lotesContainer.innerHTML = '';

                var lotes = result.lotes || [];
                var celularInput = document.getElementById('celular');

                var proyectoGroup = document.getElementById('proyecto_group');
                var mzLtGroup = document.getElementById('mz_lt_group');
                var proyectoInput = document.getElementById('proyecto');
                var mzInput = document.getElementById('mz');
                var ltInput = document.getElementById('lt');

                if (lotes.length > 0) {
                    celularInput.removeAttribute('required');
                    proyectoGroup.style.display = 'none';
                    mzLtGroup.style.display = 'none';
                    proyectoInput.removeAttribute('required');
                    mzInput.removeAttribute('required');
                    ltInput.removeAttribute('required');
                } else {
                    celularInput.setAttribute('required', 'required');
                    proyectoGroup.style.display = 'block';
                    mzLtGroup.style.display = 'flex';
                    proyectoInput.setAttribute('required', 'required');
                    mzInput.setAttribute('required', 'required');
                    ltInput.setAttribute('required', 'required');
                }

                if (lotes.length > 0) {
                    $.each(lotes, function (i, lote) {
                        var texto = lote.contrato || '';
                        if (lote.mz || lote.lote) {
                            texto = lote.contrato + ' (' + lote.mz + '-' + lote.lote + ')';
                        }

                        var $label = $('<label>').addClass('checkbox-lote');

                        var $checkbox = $('<input>').attr({
                            type: 'checkbox',
                            name: 'lotes',
                            value: lote.id,
                            'data-company': lote.company
                        });

                        var $span = $('<span>').addClass('lote-text').text(texto);

                        var $linksContainer = $('<div>').addClass('lote-links-vertical').css({
                            'display': 'flex',
                            'flex-direction': 'column',
                            'margin-left': 'auto',
                            'gap': '5px'
                        });

                        var $cronogramaLink = $('<a>')
                            .attr({
                                href: '/my/cronogramajz/download/' + lote.id,
                                title: 'Ver cronograma'
                            })
                            .addClass('lote-link-item cronograma-link')
                            .html('📋 Cronograma')
                            .css({
                                'text-decoration': 'none',
                                'font-size': '14px',
                                'padding': '4px 12px',
                                'border-radius': '4px',
                                'background-color': '#e3f2fd',
                                'color': '#0d6efd',
                                'display': 'inline-block',
                                'text-align': 'center',
                                'transition': 'all 0.2s'
                            });

                        $linksContainer.append($cronogramaLink);

                        if (lote.mora != 0) {
                            var $moraLink = $('<a>')
                                .attr({
                                    href: '/my/mora/download/' + lote.id,
                                    title: 'Ver mora'
                                })
                                .addClass('lote-link-item mora-link')
                                .html('💰 Mora S/.' + lote.mora)
                                .css({
                                    'text-decoration': 'none',
                                    'font-size': '14px',
                                    'padding': '4px 12px',
                                    'border-radius': '4px',
                                    'background-color': '#f8d7da',
                                    'color': '#dc3545',
                                    'display': 'inline-block',
                                    'text-align': 'center',
                                    'transition': 'all 0.2s'
                                });

                            $linksContainer.append($moraLink);
                        }

                        $label.append($checkbox, $span, $linksContainer);
                        $(lotesContainer).append($label);
                    });
                    lotesGroup.style.display = 'block';
                } else {
                    lotesGroup.style.display = 'none';
                }
            }
        })
        .catch(function (error) {
            console.error('Error al consultar el cliente:', error);
        });
    }

    // ===== Eventos para consultar cliente =====
    const lotesContainer = document.getElementById('lotes_container');

    lotesContainer.addEventListener('change', function (event) {
        if (event.target.type === 'checkbox' && event.target.name === 'lotes') {
            var companySeleccionado = event.target.getAttribute('data-company');

            if (event.target.checked) {
                var checkboxes = lotesContainer.querySelectorAll('input[name="lotes"]');
                checkboxes.forEach(function (cb) {
                    if (cb !== event.target && cb.getAttribute('data-company') !== companySeleccionado) {
                        cb.checked = false;
                    }
                });
            }
        }
    });

    vatInput.addEventListener('input', function () {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(consultarCliente, 600);
    });

    vatInput.addEventListener('blur', function () {
        clearTimeout(debounceTimer);
        consultarCliente();
    });

    tIdentiInput.addEventListener('change', function () {
        clearTimeout(debounceTimer);
        consultarCliente();
    });
});