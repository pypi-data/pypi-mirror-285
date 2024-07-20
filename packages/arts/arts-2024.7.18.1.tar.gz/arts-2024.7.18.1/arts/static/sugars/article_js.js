if (typeof window.host_type === 'undefined') {
    window.host_type = 0

    window.video_template = `<div><video loading="lazy" src='{{src}}' controls onclick="show('{{src}}')"></video></div>`
    window.img_template = `<div><img loading="lazy" src='{{src}}' onclick="show('{{src}}')"></div>`
    window.audio_template = `<audio loading="lazy" controls src="{{src}}"></audio>`
    
    window.big_video_template = `<video loading="lazy" src='{{src}}' controls onclick="show('{{src}}')"></video>`
    window.big_img_template = `<img loading="lazy" src='{{src}}' onclick="show('{{src}}')">`
    
    window.go_home_box = `<div class='go_home_box'>\n<button class="go_home" onclick="show('/index.html')">[作者主页]</button> 👈</div>`
    window.portrait_template = `<img class="portrait" loading="lazy" src='{{src}}'>`

    window.show = (src) => {event.preventDefault(); window.open(src, '_blank')}
    window.relative_path = decodeURIComponent(window.location.href.replace('/arts/arts/', '/arts/')).split('/arts/').at(-1)
    // window.oas1_base = decodeURIComponent(new URL('.', 'https://lcctoor.github.io/arts_static1/arts/' + relative_path).href)
    // window.oas2_base = decodeURIComponent(new URL('.', 'https://lcctoor.github.io/arts_static2/arts/' + relative_path).href)

    window.video_suffixes = ['mp4']
    window.img_suffixes = ['jpg', 'png', 'jpeg']
    window.audio_suffixes = ['flac', 'mp3', 'ogg']

    window.modify_src = (src) => {
        // if (host_type !== 3) {
        //     if (src.startsWith('oas1_')) {return oas1_base + src}
        //     else if (src.startsWith('oas2_')) {return oas2_base + src}
        // }
        return src
    }

    window.creat_media = (media) => {
        if (media) {
            let content = []
            for (let src of media) {
                let suffix = src.match(/\.([^.]+)$/)
                src = modify_src(src)
                if (suffix) {
                    suffix = suffix[1]
                    if (video_suffixes.includes(suffix))
                        {content.push(video_template.replace(/{{src}}/g, src))}
                    else if (img_suffixes.includes(suffix))
                        {content.push(img_template.replace(/{{src}}/g, src))}
                    else if (audio_suffixes.includes(suffix)) {
                        {content.push(audio_template.replace(/{{src}}/g, src))}
                    }
                }
            }
            let ele = document.createElement('div')
            ele.classList.add('ch_15')
            ele.innerHTML += content.join('\n')
            let currentScript = document.currentScript; currentScript.parentElement.insertBefore(ele, currentScript)
        }
    }
    
    window.creat_big_media = (media) => {
        if (media) {
            let content = []
            for (let src of media) {
                let suffix = src.match(/\.([^.]+)$/)
                src = modify_src(src)
                if (suffix) {
                    suffix = suffix[1]
                    if (video_suffixes.includes(suffix))
                        {content.push(big_video_template.replace(/{{src}}/g, src))}
                    else if (img_suffixes.includes(suffix))
                        {content.push(big_img_template.replace(/{{src}}/g, src))}
                    else if (audio_suffixes.includes(suffix)) {
                        {content.push(audio_template.replace(/{{src}}/g, src))}
                    }
                }
            }
            let ele = document.createElement('div')
            ele.classList.add('ch_16')
            ele.innerHTML += content.join('\n')
            let currentScript = document.currentScript; currentScript.parentElement.insertBefore(ele, currentScript)
        }
    }
    
    window.creat_portrait = (src) => {
        document.currentScript.parentElement.innerHTML += portrait_template.replace(/{{src}}/g, modify_src(src))
    }

    window.clean_text = (text) => text.replace(/\s+$/, '').replace(/[\s\\]*\\[\s\\]*/g, '')
    
    window.render = (author=true) => {
        if (! document.title) {document.title = decodeURIComponent(document.URL).match(/\/(\d*\s*-\s*)?([^/\\]+)\/?$/)[2]}
        for (let ele of document.querySelectorAll('blockquote')) {ele.innerHTML = ele.innerHTML.trim()}
        for (let ele of document.querySelectorAll('people > pre')) {ele.innerHTML = clean_text(ele.innerHTML)}
        let pre = document.querySelector('body > pre')
        if (author && window.self === window.top) {pre.innerHTML = clean_text(pre.innerHTML) + go_home_box}
        else {pre.innerHTML = clean_text(pre.innerHTML)}
        pre.addEventListener('dblclick', () => {window.open(document.URL, '_blank')})
        for (let ele of document.querySelectorAll('textarea.code')) {ele.innerHTML = ele.innerHTML.trim(); ele.style.height = ele.scrollHeight + 'px'}
    }
}

if (document.currentScript.src.includes('offline_files')) {window.host_type = 3}
else if (document.URL.startsWith('file')) {window.host_type = Math.max(window.host_type, 2)}
else {window.host_type = Math.max(window.host_type, 1)}