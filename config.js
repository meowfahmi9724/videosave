// এখানে আপনার Render ব্যাকএন্ডের লিংক বসান (শেষে / দেবেন না)
window.API_URL = "https://videosave-api.onrender.com";

// ঘরের সার্ভারের (ক্লাউডফ্লেয়ার টানেল) লিংক। ঘরের সার্ভার বন্ধ থাকলে ফাঁকা রাখুন বা লাইনটা এভাবেই রেখে দিন।
// উদাহরণ: "https://abc-def.trycloudflare.com" (শেষে / দেবেন না)
window.API_URL_HOME = "";

// Cloudflare Worker লিংক (ট্যাবের টানেল লিংক নিজে নিজে আপডেট হবে)। শেষে / দেবেন না।
window.API_REGISTRY = "https://vd-link.customboss08.workers.dev";

// এই ডিভাইসের Termux (127.0.0.1) আগে খুঁজবে কি না। ট্যাবে সার্ভার চালালে false করুন।
window.USE_LOCAL = false;
