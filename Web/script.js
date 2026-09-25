document.addEventListener('DOMContentLoaded', () => {

    window.map = L.map('map', {
        zoomAnimation: true,
        fadeAnimation: true,
        trackResize: true
    }).setView([-22.4128, -45.7973], 7);

    window.camadasAtivas = [];

    window.trocarCamada = function(urlsOuTexto) {
        const urls = typeof urlsOuTexto === 'string' ? JSON.parse(urlsOuTexto) : urlsOuTexto;

        window.camadasAtivas.forEach(function(camada) {
            window.map.removeLayer(camada);
        });
        window.camadasAtivas = [];

        window.camadasRadar.forEach(function(camada){
            window.map.removeLayer(camada);
        });

        urls.forEach(function(url) {
            const nova = L.tileLayer(url, { maxZoom: 19 }).addTo(window.map);
            window.camadasAtivas.push(nova);
        });
    };

    window.urlsFramesRadar = [];
    window.radarCarregando = false;
    window.radarPronto = false;
    window.indiceFrameRadar = 0;
    window.camadasRadar = [];
    window.radarVisivel = false;

    window.prepararRadar = async function(urlsFramesOuTexto) {
        const urlsFrames = typeof urlsFramesOuTexto === 'string' ? JSON.parse(urlsFramesOuTexto) : urlsFramesOuTexto;

        window.camadasRadar.forEach(function(camada) {
            window.map.removeLayer(camada);
        });
        window.camadasRadar = [];

        window.urlsFramesRadar = urlsFrames;
        window.radarCarregando = true;
        window.radarPronto = false;
        window.indiceFrameRadar = 0;

        console.log("RADAR: iniciando pré-carregamento de " + urlsFrames.length + " frames");

        const tamanhoLoteCamadas = 1;

        for (let inicio = 0; inicio < urlsFrames.length; inicio += tamanhoLoteCamadas) {
            const fim = Math.min(inicio + tamanhoLoteCamadas, urlsFrames.length);

            console.log("RADAR: criando camadas " + inicio + " até " + (fim - 1));

            const carregamentosCamadas = [];

            for (let indice = inicio; indice < fim; indice++) {
                const url = urlsFrames[indice];

                const camada = L.tileLayer(url, {
                    minZoom: 1,
                    maxZoom: 7,
                    opacity: 0,
                    zIndex: 100 + indice
                });

                window.camadasRadar.push(camada);

                const carregamento = new Promise(function(resolve) {
                    camada.once('load', function() {
                        console.log("RADAR: camada " + indice + " carregada");
                        resolve();
                    });

                    camada.once('tileerror', function() {
                        console.log("RADAR: camada " + indice + " teve erro em tile");
                    });
                });

                camada.addTo(window.map);

                carregamentosCamadas.push(carregamento);
            }

            await Promise.all(carregamentosCamadas);
            await new Promise(resolve => setTimeout(resolve, 300));
        }

        window.radarCarregando = false;
        window.radarPronto = true;
        window.indiceFrameRadar = 0;

        console.log("RADAR: todos os frames estão prontos!");

        if (window.qtRadarPronto) {
            window.qtRadarPronto();
        }
    };

    window.exibirRadar = function(urlsBaseOuTexto) {
        const urlsBase = typeof urlsBaseOuTexto === 'string' ? JSON.parse(urlsBaseOuTexto) : urlsBaseOuTexto;

        window.camadasAtivas.forEach(function(camada) {
            window.map.removeLayer(camada);
        });
        window.camadasAtivas = [];

        urlsBase.forEach(function(url) {
            const nova = L.tileLayer(url, { maxZoom: 19 }).addTo(window.map);
            window.camadasAtivas.push(nova);
        });

        window.camadasRadar.forEach(function(camada, i) {
            if (!window.map.hasLayer(camada)) {
                camada.addTo(window.map);
            }
            camada.setOpacity(i === window.indiceFrameRadar ? 1 : 0);
            camada.bringToFront();
        });

        window.radarVisivel = true;
    };

    window.avancarFrameRadar = function(indice) {
        if (!window.radarPronto) {
            console.log("RADAR: frames ainda não estão prontos.");
            return;
        }

        if (indice < 0 || indice >= window.camadasRadar.length) {
            console.log("RADAR: índice inválido: " + indice);
            return;
        }

        const indiceAnterior = window.indiceFrameRadar;

        if (window.camadasRadar[indiceAnterior]) {
            window.camadasRadar[indiceAnterior].setOpacity(0);
        }

        window.camadasRadar[indice].setOpacity(1);
        window.indiceFrameRadar = indice;
        window.camadasRadar[indice].bringToFront();

        console.log("RADAR: exibindo frame " + indice);
    };

    window.marcador = null;

    window.colocarMarcador = function(lat, lng) {
        if (window.marcador) {
            window.map.removeLayer(window.marcador);
        }

        const iconePersonalizado = L.divIcon({
            className: 'marcador-customizado',
            html: '<div style="background-color: #3498db; width: 16px; height: 16px; border-radius: 50%; border: 2px solid white;"></div>',
            iconSize: [16, 16],
            iconAnchor: [8, 8]
        });

        window.marcador = L.marker([lat, lng], { icon: iconePersonalizado }).addTo(window.map);
    };

    window.map.on('click', function(e) {
        const lat = e.latlng.lat;
        const lng = e.latlng.lng;

        window.colocarMarcador(lat, lng);

        console.log(`LOCATION_SELECTED:${lat},${lng}`);
    });

    const fixMapSize = () => {
        if (window.map) {
            window.map.invalidateSize();
        }
    };
    setTimeout(fixMapSize, 200);
    setTimeout(fixMapSize, 600);
    window.addEventListener('resize', fixMapSize);
});

    window.bloquearMapa = function() {
        window.map.dragging.disable();
        window.map.touchZoom.disable();
        window.map.doubleClickZoom.disable();
        window.map.scrollWheelZoom.disable();
        window.map.boxZoom.disable();
        window.map.keyboard.disable();
        if (window.map.tap) window.map.tap.disable();

    };

    window.liberarMapa = function() {
        window.map.dragging.enable();
        window.map.touchZoom.enable();
        window.map.doubleClickZoom.enable();
        window.map.scrollWheelZoom.enable();
        window.map.boxZoom.enable();
        window.map.keyboard.enable();
        if (window.map.tap) window.map.tap.enable();

    };