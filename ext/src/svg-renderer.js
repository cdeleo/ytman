(function (global, factory) {
    global.SvgRenderer = factory();
}(this, (function () {
    class SvgRenderer {
        constructor(templatePath, background) {
            this.templateStr = fetch(templatePath).then(response => response.text());
        }

        async _loadSvgStr(svgStr) {
            const img = new Image();
            const svg = new Blob([svgStr], { type: 'image/svg+xml;charset=utf-8' });
            const url = window.URL.createObjectURL(svg);

            const loaded = new Promise(resolve => {
                img.onload = () => resolve([img, () => { window.URL.revokeObjectURL(url) }]);
            });
            img.src = url;
            return loaded;
        }

        _fillTemplate(template, valueMap) {
            let filled = template;
            for (const key in valueMap) {
                filled = filled.replaceAll('{' + key + '}', valueMap[key]);
            }
            return filled;
        }

        async render(c, background, valueMap) {
            const filledTemplateStr = this._fillTemplate(await this.templateStr, valueMap);
            const [template, cleanup] = await this._loadSvgStr(filledTemplateStr);

            if (background) {
                c.drawImage(await background, 0, 0, 1280, 720);
            }
            c.drawImage(template, 0, 0);
            cleanup();
        }
    }

    return SvgRenderer;
})));