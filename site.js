/* UltraVideoDownloader website: translations, language switcher, download button, anonymous stats. */
(function(){
var REPO='https://github.com/oussamakhouya73/UltraVideoDownloader';
var BASE=REPO+'/releases/latest/download/';
var T={
en:{
 h1_1:'Any video.',h1_2:'Any length.',h1_3:'Any size.',
 lede:'UltraVideoDownloader saves videos in the best quality they offer. It runs on your own computer, so nothing is uploaded to a server and nothing is capped.',
 dl_win:'Download for Windows',dl_android:'Get the Android app',dl_mac:'Download for macOS',dl_linux:'Download for Linux',other:'Other devices',
 fine:'Free. Run the installer and you get a desktop icon and a Start menu entry. Windows may show a blue warning because the app is new: choose More info, then Run anyway.',
 devices_h:'Pick your device',
 win_p:'Own window, own icon, updates itself. Windows 10 and 11.',win_get:'Download the installer',win_zip:'Portable zip',
 and_p:'Our own Android app is coming. Until then, these free, open-source apps do the same job.',
 mac_p:'Opens in your browser. The first time, right-click the file and choose Open.',linux_p:'Opens in your browser. Make the file executable with chmod +x, then run it.',dl_zip:'Download the zip',
 steps_h:'Three steps',
 s1b:'Download and install',s1t:'Pick your device above and open the file. On Windows the installer adds a desktop shortcut.',
 s2b:'Open the app',s2t:'A window opens with an empty link box. Light and dark themes are built in.',
 s3b:'Paste a link and press Download',s3t:'The app checks the link and shows the video. It picks the best quality the video really has. Press Save to… to choose the folder. You can pause, and it continues where it stopped, even after the internet drops or you close the app.',
 f1h:'The real best quality',f1p:'If a video has 720p, you get 720p. If it has 4K, you get 4K. You can still pick a lower one.',
 f2h:'Many gigabytes is fine',f2p:'Your computer does the work, so there is no limit on length or file size.',
 f3h:'Your links stay with you',f3p:'No account. Nothing you paste is sent to us. The app only counts anonymous usage, and you can switch that off in Settings.',
 foot:'Use it for videos you own or have permission to download. The rules of the site a video comes from still apply.',privacy:'Privacy',ad:'Advertisement',
 p_title:'Privacy',p_updated:'Last updated: November 2026',
 p1h:'The app',p1p:'UltraVideoDownloader runs on your own device. The links you paste and the videos you save stay on your device. We do not run a server that receives your links, and we do not ask you to create an account.',
 p2h:'Anonymous usage statistics',p2p:'To know how many people use the app and to fix problems, the app sends a few anonymous facts: a random install number (not linked to you), the app version, your operating system, your language, your country (worked out from your IP address, which is not stored), how long the app stays open, and how many downloads started, finished or failed. It never sends the links you paste, video titles or file names. It is on by default, and you can switch it off any time in Settings. The website counts visits in the same anonymous way and uses no cookies. We use PostHog to process these statistics.',
 p3h:'Ads',p3p:'This website and the app show ads from third-party advertising networks. These networks can use cookies and similar identifiers to show ads and to measure them. They may collect information such as your IP address, browser type and the pages you view. We do not control what they collect. Please read the privacy policy of the network that serves the ad you see. Ads are shown in a separate frame, so the ad code cannot read the links you paste.',
 p4h:'Your choices',p4p:'You can block or delete cookies in your browser settings, and you can use an ad blocker. The app works the same without ads. Turn off statistics in the app Settings.',
 p5h:'Hosting',p5p:'The website is a static page. The hosting provider may keep standard server logs, such as IP address and time of visit, for security and operation.',
 p6h:'Downloading content',p6p:'Use the app only for videos you own or have permission to save. The terms of the site a video comes from still apply.',
 p7h:'Contact',p7p:'Questions about privacy? Open an issue on our GitHub page.',p7l:'GitHub'},
ar:{
 h1_1:'أي فيديو.',h1_2:'أي مدة.',h1_3:'أي حجم.',
 lede:'يحفظ UltraVideoDownloader الفيديو بأفضل جودة يوفرها. يعمل على جهازك أنت، فلا شيء يُرفع إلى خادم ولا شيء له حد أقصى.',
 dl_win:'تنزيل لنظام ويندوز',dl_android:'احصل على تطبيق أندرويد',dl_mac:'تنزيل لنظام ماك',dl_linux:'تنزيل للينكس',other:'أجهزة أخرى',
 fine:'مجاني. شغّل المثبّت لتحصل على أيقونة على سطح المكتب وعلى قائمة ابدأ. قد يعرض ويندوز تحذيرا أزرق لأن التطبيق جديد: اختر «مزيد من المعلومات» ثم «تشغيل على أي حال».',
 devices_h:'اختر جهازك',
 win_p:'نافذة خاصة وأيقونة خاصة، ويحدّث نفسه. ويندوز 10 و11.',win_get:'تنزيل المثبّت',win_zip:'نسخة محمولة (zip)',
 and_p:'تطبيق أندرويد الخاص بنا قادم قريبا. إلى ذلك الحين، هذه تطبيقات مجانية ومفتوحة المصدر تؤدي المهمة نفسها.',
 mac_p:'يفتح في المتصفح. في المرة الأولى انقر بزر الفأرة الأيمن على الملف واختر «فتح».',linux_p:'يفتح في المتصفح. اجعل الملف قابلا للتنفيذ بالأمر chmod +x ثم شغّله.',dl_zip:'تنزيل ملف zip',
 steps_h:'ثلاث خطوات',
 s1b:'نزّل وثبّت',s1t:'اختر جهازك أعلاه وافتح الملف. على ويندوز يضيف المثبّت اختصارا على سطح المكتب.',
 s2b:'افتح التطبيق',s2t:'تظهر نافذة فيها خانة رابط فارغة. الوضعان الفاتح والداكن متوفران.',
 s3b:'الصق الرابط واضغط تنزيل',s3t:'يفحص التطبيق الرابط ويعرض الفيديو ويختار أفضل جودة يملكها الفيديو فعلا. اضغط «حفظ في…» لتختار المجلد. يمكنك الإيقاف المؤقت، ويكمل من حيث توقف حتى لو انقطع الإنترنت أو أغلقت التطبيق.',
 f1h:'أفضل جودة حقيقية',f1p:'إذا كان الفيديو بجودة 720 تحصل على 720، وإذا كان 4K تحصل على 4K. ويمكنك اختيار جودة أقل.',
 f2h:'غيغابايتات كثيرة لا مشكلة',f2p:'جهازك هو الذي يعمل، لذلك لا حد لطول الفيديو ولا لحجم الملف.',
 f3h:'روابطك تبقى عندك',f3p:'بلا حساب. لا يُرسل إلينا أي رابط تلصقه. يحصي التطبيق الاستعمال دون هوية فقط، ويمكنك إيقاف ذلك من الإعدادات.',
 foot:'استعمله للفيديوهات التي تملكها أو لديك إذن بتنزيلها. وتبقى قواعد الموقع الذي يأتي منه الفيديو سارية.',privacy:'الخصوصية',ad:'إعلان',
 p_title:'الخصوصية',p_updated:'آخر تحديث: نوفمبر 2026',
 p1h:'التطبيق',p1p:'يعمل UltraVideoDownloader على جهازك. الروابط التي تلصقها والفيديوهات التي تحفظها تبقى على جهازك. ليس لدينا خادم يستقبل روابطك، ولا نطلب منك إنشاء حساب.',
 p2h:'إحصائيات استعمال مجهولة',p2p:'لمعرفة عدد مستعملي التطبيق ولإصلاح المشاكل، يرسل التطبيق بعض المعلومات دون هوية: رقم تثبيت عشوائي (غير مرتبط بك)، ونسخة التطبيق، ونظام التشغيل، واللغة، والبلد (يُستنتج من عنوان IP الذي لا يُخزَّن)، ومدة بقاء التطبيق مفتوحا، وعدد التنزيلات التي بدأت أو انتهت أو فشلت. لا يرسل أبدا الروابط التي تلصقها ولا عناوين الفيديوهات ولا أسماء الملفات. هذه الميزة مفعّلة افتراضيا، ويمكنك إيقافها في أي وقت من الإعدادات. يحصي الموقع الزيارات بالطريقة المجهولة نفسها ولا يستعمل ملفات تعريف الارتباط. نستعمل PostHog لمعالجة هذه الإحصائيات.',
 p3h:'الإعلانات',p3p:'يعرض هذا الموقع والتطبيق إعلانات من شبكات إعلانية خارجية. قد تستعمل هذه الشبكات ملفات تعريف الارتباط ومعرّفات مشابهة لعرض الإعلانات وقياسها، وقد تجمع معلومات مثل عنوان IP ونوع المتصفح والصفحات التي تشاهدها. نحن لا نتحكم فيما تجمعه. يرجى قراءة سياسة الخصوصية للشبكة التي تعرض الإعلان. تُعرض الإعلانات في إطار منفصل، فلا يستطيع كود الإعلان قراءة الروابط التي تلصقها.',
 p4h:'خياراتك',p4p:'يمكنك حظر ملفات تعريف الارتباط أو حذفها من إعدادات المتصفح، ويمكنك استعمال مانع إعلانات. يعمل التطبيق بالطريقة نفسها بدون إعلانات. أوقف الإحصائيات من إعدادات التطبيق.',
 p5h:'الاستضافة',p5p:'الموقع صفحة ثابتة. قد يحتفظ مزود الاستضافة بسجلات خادم عادية، مثل عنوان IP ووقت الزيارة، لأغراض الأمان والتشغيل.',
 p6h:'تنزيل المحتوى',p6p:'استعمل التطبيق فقط للفيديوهات التي تملكها أو لديك إذن بحفظها. وتبقى شروط الموقع الذي يأتي منه الفيديو سارية.',
 p7h:'التواصل',p7p:'أسئلة عن الخصوصية؟ افتح مسألة (issue) في صفحتنا على GitHub.',p7l:'GitHub'},
fr:{
 h1_1:'Toute vidéo.',h1_2:'Toute durée.',h1_3:'Toute taille.',
 lede:'UltraVideoDownloader enregistre les vidéos dans la meilleure qualité qu’elles proposent. Il tourne sur votre ordinateur : rien n’est envoyé à un serveur et rien n’est plafonné.',
 dl_win:'Télécharger pour Windows',dl_android:'Obtenir l’appli Android',dl_mac:'Télécharger pour macOS',dl_linux:'Télécharger pour Linux',other:'Autres appareils',
 fine:'Gratuit. Lancez l’installateur : vous obtenez une icône sur le bureau et une entrée dans le menu Démarrer. Windows peut afficher un avertissement bleu car l’appli est récente : choisissez Informations complémentaires, puis Exécuter quand même.',
 devices_h:'Choisissez votre appareil',
 win_p:'Fenêtre et icône à elle, se met à jour toute seule. Windows 10 et 11.',win_get:'Télécharger l’installateur',win_zip:'Zip portable',
 and_p:'Notre propre appli Android arrive. En attendant, ces applis gratuites et open source font le même travail.',
 mac_p:'S’ouvre dans votre navigateur. La première fois, clic droit sur le fichier puis Ouvrir.',linux_p:'S’ouvre dans votre navigateur. Rendez le fichier exécutable avec chmod +x, puis lancez-le.',dl_zip:'Télécharger le zip',
 steps_h:'Trois étapes',
 s1b:'Télécharger et installer',s1t:'Choisissez votre appareil ci-dessus et ouvrez le fichier. Sous Windows, l’installateur ajoute un raccourci sur le bureau.',
 s2b:'Ouvrir l’appli',s2t:'Une fenêtre s’ouvre avec une case de lien vide. Thèmes clair et sombre inclus.',
 s3b:'Coller un lien et appuyer sur Télécharger',s3t:'L’appli vérifie le lien et affiche la vidéo. Elle choisit la meilleure qualité réellement disponible. Appuyez sur Enregistrer dans… pour choisir le dossier. Vous pouvez mettre en pause, et ça reprend là où ça s’est arrêté, même après une coupure d’internet ou la fermeture de l’appli.',
 f1h:'La vraie meilleure qualité',f1p:'Si la vidéo existe en 720p, vous obtenez du 720p. Si elle existe en 4K, vous obtenez de la 4K. Vous pouvez toujours en choisir une plus basse.',
 f2h:'Plusieurs gigaoctets, aucun souci',f2p:'C’est votre ordinateur qui travaille : aucune limite de durée ni de taille de fichier.',
 f3h:'Vos liens restent chez vous',f3p:'Pas de compte. Rien de ce que vous collez ne nous est envoyé. L’appli compte seulement l’usage de façon anonyme, et vous pouvez le désactiver dans les Réglages.',
 foot:'À utiliser pour des vidéos qui vous appartiennent ou que vous avez le droit de télécharger. Les règles du site d’origine s’appliquent toujours.',privacy:'Confidentialité',ad:'Publicité',
 p_title:'Confidentialité',p_updated:'Dernière mise à jour : novembre 2026',
 p1h:'L’appli',p1p:'UltraVideoDownloader fonctionne sur votre appareil. Les liens que vous collez et les vidéos que vous enregistrez restent sur votre appareil. Nous n’avons pas de serveur qui reçoit vos liens et nous ne vous demandons pas de créer un compte.',
 p2h:'Statistiques d’usage anonymes',p2p:'Pour savoir combien de personnes utilisent l’appli et corriger les problèmes, l’appli envoie quelques informations anonymes : un numéro d’installation aléatoire (non lié à vous), la version de l’appli, votre système, votre langue, votre pays (déduit de votre adresse IP, qui n’est pas conservée), la durée d’ouverture de l’appli, et le nombre de téléchargements démarrés, terminés ou échoués. Elle n’envoie jamais les liens collés, les titres des vidéos ni les noms de fichiers. C’est activé par défaut et vous pouvez le désactiver à tout moment dans les Réglages. Le site compte les visites de la même façon anonyme et n’utilise aucun cookie. Nous utilisons PostHog pour traiter ces statistiques.',
 p3h:'Publicités',p3p:'Ce site et l’appli affichent des publicités de réseaux publicitaires tiers. Ces réseaux peuvent utiliser des cookies et des identifiants similaires pour afficher et mesurer les publicités. Ils peuvent collecter des informations comme votre adresse IP, votre navigateur et les pages consultées. Nous ne contrôlons pas ce qu’ils collectent. Veuillez lire la politique de confidentialité du réseau qui diffuse la publicité. Les publicités sont affichées dans un cadre séparé : leur code ne peut pas lire les liens que vous collez.',
 p4h:'Vos choix',p4p:'Vous pouvez bloquer ou supprimer les cookies dans votre navigateur et utiliser un bloqueur de publicités. L’appli fonctionne de la même façon sans publicités. Désactivez les statistiques dans les Réglages de l’appli.',
 p5h:'Hébergement',p5p:'Le site est une page statique. L’hébergeur peut conserver des journaux de serveur standard, comme l’adresse IP et l’heure de visite, pour la sécurité et le fonctionnement.',
 p6h:'Téléchargement de contenu',p6p:'Utilisez l’appli uniquement pour des vidéos qui vous appartiennent ou que vous avez le droit d’enregistrer. Les conditions du site d’origine s’appliquent toujours.',
 p7h:'Contact',p7p:'Une question sur la confidentialité ? Ouvrez un ticket sur notre page GitHub.',p7l:'GitHub'},
es:{
 h1_1:'Cualquier vídeo.',h1_2:'Cualquier duración.',h1_3:'Cualquier tamaño.',
 lede:'UltraVideoDownloader guarda los vídeos en la mejor calidad que ofrecen. Funciona en tu propio equipo, así que nada se sube a un servidor y nada tiene tope.',
 dl_win:'Descargar para Windows',dl_android:'Obtener la app de Android',dl_mac:'Descargar para macOS',dl_linux:'Descargar para Linux',other:'Otros dispositivos',
 fine:'Gratis. Ejecuta el instalador y tendrás un icono en el escritorio y una entrada en el menú Inicio. Windows puede mostrar un aviso azul porque la app es nueva: elige Más información y luego Ejecutar de todas formas.',
 devices_h:'Elige tu dispositivo',
 win_p:'Ventana e icono propios, se actualiza sola. Windows 10 y 11.',win_get:'Descargar el instalador',win_zip:'Zip portátil',
 and_p:'Nuestra propia app de Android llegará pronto. Mientras tanto, estas apps gratuitas y de código abierto hacen el mismo trabajo.',
 mac_p:'Se abre en el navegador. La primera vez, clic derecho sobre el archivo y elige Abrir.',linux_p:'Se abre en el navegador. Haz el archivo ejecutable con chmod +x y ejecútalo.',dl_zip:'Descargar el zip',
 steps_h:'Tres pasos',
 s1b:'Descargar e instalar',s1t:'Elige tu dispositivo arriba y abre el archivo. En Windows, el instalador añade un acceso directo al escritorio.',
 s2b:'Abrir la app',s2t:'Se abre una ventana con la casilla del enlace vacía. Incluye tema claro y oscuro.',
 s3b:'Pegar un enlace y pulsar Descargar',s3t:'La app comprueba el enlace y muestra el vídeo. Elige la mejor calidad que el vídeo tiene de verdad. Pulsa Guardar en… para elegir la carpeta. Puedes pausar, y continúa donde se quedó, incluso si se corta internet o cierras la app.',
 f1h:'La mejor calidad real',f1p:'Si el vídeo tiene 720p, obtienes 720p. Si tiene 4K, obtienes 4K. Aun así puedes elegir una más baja.',
 f2h:'Muchos gigabytes, sin problema',f2p:'Trabaja tu equipo, así que no hay límite de duración ni de tamaño de archivo.',
 f3h:'Tus enlaces se quedan contigo',f3p:'Sin cuenta. Nada de lo que pegas nos llega. La app solo cuenta el uso de forma anónima, y puedes desactivarlo en Ajustes.',
 foot:'Úsalo para vídeos que son tuyos o que tienes permiso para descargar. Las normas del sitio de origen siguen aplicándose.',privacy:'Privacidad',ad:'Publicidad',
 p_title:'Privacidad',p_updated:'Última actualización: noviembre de 2026',
 p1h:'La app',p1p:'UltraVideoDownloader funciona en tu propio dispositivo. Los enlaces que pegas y los vídeos que guardas se quedan en tu dispositivo. No tenemos un servidor que reciba tus enlaces y no te pedimos crear una cuenta.',
 p2h:'Estadísticas de uso anónimas',p2p:'Para saber cuánta gente usa la app y corregir problemas, la app envía algunos datos anónimos: un número de instalación aleatorio (no vinculado a ti), la versión de la app, tu sistema operativo, tu idioma, tu país (deducido de tu dirección IP, que no se guarda), cuánto tiempo permanece abierta la app y cuántas descargas empezaron, terminaron o fallaron. Nunca envía los enlaces que pegas, los títulos de los vídeos ni los nombres de archivo. Está activado por defecto y puedes desactivarlo cuando quieras en Ajustes. El sitio web cuenta las visitas de la misma forma anónima y no usa cookies. Usamos PostHog para procesar estas estadísticas.',
 p3h:'Anuncios',p3p:'Este sitio y la app muestran anuncios de redes publicitarias de terceros. Estas redes pueden usar cookies e identificadores similares para mostrar y medir los anuncios, y pueden recopilar información como tu dirección IP, el tipo de navegador y las páginas que ves. No controlamos lo que recopilan. Lee la política de privacidad de la red que muestra el anuncio. Los anuncios se muestran en un marco aparte, así que su código no puede leer los enlaces que pegas.',
 p4h:'Tus opciones',p4p:'Puedes bloquear o borrar las cookies en los ajustes del navegador y usar un bloqueador de anuncios. La app funciona igual sin anuncios. Desactiva las estadísticas en los Ajustes de la app.',
 p5h:'Alojamiento',p5p:'El sitio es una página estática. El proveedor de alojamiento puede conservar registros de servidor estándar, como la dirección IP y la hora de la visita, por seguridad y funcionamiento.',
 p6h:'Descarga de contenido',p6p:'Usa la app solo para vídeos que son tuyos o que tienes permiso para guardar. Los términos del sitio de origen siguen aplicándose.',
 p7h:'Contacto',p7p:'¿Preguntas sobre privacidad? Abre una incidencia en nuestra página de GitHub.',p7l:'GitHub'}
};
var NAMES={en:'English',ar:'العربية',fr:'Français',es:'Español'};
function store(k,v){try{if(v===undefined)return localStorage.getItem(k);localStorage.setItem(k,v)}catch(e){return null}}
function pick(){
 var q=(location.search.match(/[?&]lang=(\w\w)/)||[])[1];
 var l=q||store('uvd_lang')||(navigator.language||'en').slice(0,2).toLowerCase();
 return T[l]?l:'en';
}
var os='win';
(function(){var ua=navigator.userAgent||'';if(/Android/i.test(ua))os='android';else if(/Mac/i.test(ua)&&!/iPhone|iPad/i.test(ua))os='mac';else if(/Linux/i.test(ua))os='linux'})();
var MAIN={win:[BASE+'UltraVideoDownloader-Setup.exe','dl_win'],android:['https://github.com/deniscerri/ytdlnis/releases/latest','dl_android'],mac:[BASE+'UltraVideoDownloader-macos.zip','dl_mac'],linux:[BASE+'UltraVideoDownloader-linux.zip','dl_linux']};
function apply(l){
 var d=T[l];document.documentElement.lang=l;document.documentElement.dir=l==='ar'?'rtl':'ltr';
 [].forEach.call(document.querySelectorAll('[data-i]'),function(e){if(d[e.dataset.i])e.textContent=d[e.dataset.i]});
 var b=document.getElementById('main-dl');if(b){b.href=MAIN[os][0];b.textContent=d[MAIN[os][1]];b.dataset.platform=os}
 var tl=document.getElementById('p-title');if(tl)document.title=d.p_title+' · UltraVideoDownloader';
 var sel=document.getElementById('lang');if(sel)sel.value=l;
}
function init(){
 var sel=document.getElementById('lang');
 if(sel){Object.keys(NAMES).forEach(function(k){var o=document.createElement('option');o.value=k;o.textContent=NAMES[k];sel.appendChild(o)});
  sel.addEventListener('change',function(){store('uvd_lang',sel.value);apply(sel.value);track('language_changed',{language:sel.value})})}
 apply(pick());
}

/* ---- anonymous statistics (PostHog), no cookies, respects Do Not Track ---- */
var C=window.UVD_CONFIG||{};
var DNT=navigator.doNotTrack==='1'||window.doNotTrack==='1';
function rid(){var a=new Uint8Array(12);(window.crypto||{getRandomValues:function(x){for(var i=0;i<x.length;i++)x[i]=Math.random()*256}}).getRandomValues(a);return [].map.call(a,function(x){return('0'+x.toString(16)).slice(-2)}).join('')}
var did=store('uvd_id');if(!did){did=rid();store('uvd_id',did)}
var sid=rid(),t0=Date.now();
function track(ev,props){
 if(!C.POSTHOG_KEY||DNT)return;
 var p=Object.assign({$current_url:location.origin+location.pathname,$referrer:document.referrer?new URL(document.referrer).origin:'',$session_id:sid,$lib:'uvd-site',language:document.documentElement.lang,$process_person_profile:false,$screen_width:screen.width},props||{});
 try{fetch((C.POSTHOG_HOST||'https://eu.i.posthog.com')+'/capture/',{method:'POST',keepalive:true,headers:{'Content-Type':'application/json'},body:JSON.stringify({api_key:C.POSTHOG_KEY,event:ev,distinct_id:did,properties:p,timestamp:new Date().toISOString()})}).catch(function(){})}catch(e){}
}
document.addEventListener('click',function(e){
 var a=e.target.closest&&e.target.closest('a[href]');if(!a)return;
 var h=a.getAttribute('href')||'';
 if(/releases\/latest/.test(h)||a.id==='main-dl')track('download_click',{platform:a.dataset.platform||(/Setup\.exe|windows/i.test(h)?'win':/macos/i.test(h)?'mac':/linux/i.test(h)?'linux':/ytdlnis|seal/i.test(h)?'android-alt':'other'),href:h.slice(0,200)});
});
var left=false;
function leave(){if(left)return;left=true;track('$pageleave',{duration_seconds:Math.round((Date.now()-t0)/1000)})}
addEventListener('pagehide',leave);
document.addEventListener('visibilitychange',function(){if(document.visibilityState==='hidden')leave();else left=false});

init();track('$pageview');
})();
