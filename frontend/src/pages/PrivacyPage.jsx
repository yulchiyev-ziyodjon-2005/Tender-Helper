import LegalPageLayout from '../components/legal/LegalPageLayout';

const sections = [
  {
    id: 'scope',
    title: '1. Qo‘llanish sohasi',
    content: (
      <p>
        Ushbu Maxfiylik siyosati Tender-Helper AI platformasi va uning rasmiy
        domeni <a href="https://tenderhelperai.com" className="font-bold text-blue-600 dark:text-cyan-300">https://tenderhelperai.com</a> orqali
        taqdim etiladigan autentifikatsiya, tender tahlili, jamoaviy ish va
        hujjat xizmatlariga taalluqlidir.
      </p>
    ),
  },
  {
    id: 'information',
    title: '2. Yig‘iladigan ma’lumotlar',
    content: (
      <>
        <p>Hisob yaratish va xizmatni taqdim etish uchun quyidagi ma’lumotlar qayta ishlanishi mumkin:</p>
        <ul className="list-disc space-y-2 pl-5">
          <li>to‘liq ism;</li>
          <li>korporativ email manzili;</li>
          <li>telefon raqami va SMS tasdiqlash holati;</li>
          <li>ixtiyoriy kompaniya STIR (TIN) identifikatori;</li>
          <li>kompaniya profili, rollar, jamoa a’zoligi va foydalanish metrikalari;</li>
          <li>tender so‘rovlari, tahlil natijalari va xavfsizlik audit hodisalari.</li>
        </ul>
      </>
    ),
  },
  {
    id: 'purpose',
    title: '3. Qayta ishlash maqsadlari',
    content: (
      <p>
        Ma’lumotlar foydalanuvchini autentifikatsiya qilish, kompaniya
        vakolatlarini tekshirish, tenderlarni moslashtirish, AI tahlilini
        yaratish, obuna cheklovlarini boshqarish, firibgarlikni aniqlash,
        xizmat ko‘rsatish va qonuniy majburiyatlarni bajarish uchun ishlatiladi.
      </p>
    ),
  },
  {
    id: 'security',
    title: '4. Ma’lumotlarni himoya qilish tamoyillari',
    content: (
      <>
        <p>
          Platforma kriptografik sessiya tokenlari, token versiyalash va
          autentifikatsiya muddatlari orqali sessiya yaxlitligini himoya qiladi.
          Frontend XSS himoya qatlami foydalanuvchi matnini xavfsiz render qilish,
          markup va nazorat belgilarini cheklash hamda xavfli HTML kiritilishini
          oldini olish tamoyillariga asoslanadi.
        </p>
        <p>
          Tokenlar va foydalanuvchi holati ichki storage standartlariga qat’iy
          muvofiq saqlanadi: qisqa sessiyalar session storage’da, foydalanuvchi
          aniq tanlagan davomiy sessiyalar esa cheklangan local storage’da
          saqlanadi. Maxfiy server kalitlari brauzer storage’iga yozilmaydi.
        </p>
      </>
    ),
  },
  {
    id: 'sharing',
    title: '5. Uchinchi tomon xizmatlari',
    content: (
      <p>
        Google OAuth, SMS, email, hosting, ma’lumotlar bazasi va AI providerlari
        faqat xizmat uchun zarur ma’lumotlarni o‘zlarining shartlari asosida
        qayta ishlashi mumkin. Tender-Helper AI shaxsiy ma’lumotlarni reklama
        maqsadida sotmaydi.
      </p>
    ),
  },
  {
    id: 'retention',
    title: '6. Saqlash muddati va foydalanuvchi huquqlari',
    content: (
      <p>
        Ma’lumotlar faol hisob, audit, xavfsizlik va qonuniy majburiyatlar uchun
        zarur muddat saqlanadi. Foydalanuvchi o‘z ma’lumotlariga kirish, ularni
        tuzatish yoki qonun ruxsat bergan doirada o‘chirish bo‘yicha
        info@tenderhelperai.com manziliga murojaat qilishi mumkin.
      </p>
    ),
  },
  {
    id: 'changes',
    title: '7. Siyosatdagi o‘zgarishlar',
    content: (
      <p>
        Muhim o‘zgarishlar ushbu sahifada yangilangan sana bilan e’lon qilinadi.
        Platformadan o‘zgarish kuchga kirgandan keyin foydalanish yangilangan
        siyosat bilan tanishilganini anglatadi.
      </p>
    ),
  },
];

export default function PrivacyPage() {
  return (
    <LegalPageLayout
      eyebrow="Legal · Privacy Policy"
      title="Maxfiylik siyosati"
      summary="Tender-Helper AI foydalanuvchi va kompaniya ma’lumotlarini xizmatni xavfsiz taqdim etish uchun minimal, maqsadga muvofiq va nazorat qilinadigan shaklda qayta ishlaydi."
      lastUpdated="June 15, 2026"
      sections={sections}
    />
  );
}
