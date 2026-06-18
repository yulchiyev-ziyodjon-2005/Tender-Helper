import LegalPageLayout from '../components/legal/LegalPageLayout';

const sections = [
  {
    id: 'agreement',
    title: '1. Shartlarni qabul qilish',
    content: (
      <p>
        https://tenderhelperai.com platformasida hisob yaratish yoki xizmatdan
        foydalanish orqali foydalanuvchi ushbu shartlarga va amaldagi Maxfiylik
        siyosatiga rozilik bildiradi. Tashkilot nomidan ro‘yxatdan o‘tgan shaxs
        tegishli vakolatga ega ekanini tasdiqlaydi.
      </p>
    ),
  },
  {
    id: 'subscriptions',
    title: '2. Obuna tariflari',
    content: (
      <>
        <p>
          Free Tier asosiy qidiruv va belgilangan fair-use limitidagi
          funksiyalarni taqdim etadi. Limitlar davriy ravishda yangilanishi va
          mahsulot interfeysida ko‘rsatilishi mumkin.
        </p>
        <p>
          Business Tier kengaytirilgan hujjat, jamoa va intelligence
          funksiyalarini taqdim etadi hamda haqiqiy kompaniya STIR
          verifikatsiyasini majburiy talab qiladi. Noto‘g‘ri, boshqa tashkilotga
          tegishli yoki tasdiqlanmagan STIR Business funksiyalarini faollashtirmaydi.
        </p>
      </>
    ),
  },
  {
    id: 'teams',
    title: '3. User seat va jamoa vakolatlari',
    content: (
      <>
        <p>
          Pullik tariflarda user seat soni obuna, buyurtma yoki tashkilot
          sozlamalariga qarab dinamik boshqariladi. Seat qo‘shilishi billing va
          entitlement holatiga ta’sir qilishi mumkin.
        </p>
        <p>
          Jamoa avtorizatsiyasi Owner, Manager, Analyst va Viewer kabi ko‘p
          rolli cheklovlarga asoslanadi. Har bir rol faqat berilgan permission
          doirasida ma’lumot ko‘rishi yoki o‘zgartirishi mumkin. Administrator
          takliflar, rollar, seatlar va sobiq xodim kirishini o‘z vaqtida
          boshqarish uchun javobgardir.
        </p>
      </>
    ),
  },
  {
    id: 'acceptable-use',
    title: '4. Hisob xavfsizligi va maqbul foydalanish',
    content: (
      <p>
        Login ma’lumotlarini ulashish, boshqa tashkilot ma’lumotiga ruxsatsiz
        kirish, zararli fayl yuklash, rate limit yoki xavfsizlik nazoratlarini
        chetlab o‘tish taqiqlanadi. Shubhali faoliyat hisobning vaqtincha
        cheklanishiga yoki yopilishiga olib kelishi mumkin.
      </p>
    ),
  },
  {
    id: 'ai-disclaimer',
    title: '5. AI va hujjat eksporti bo‘yicha javobgarlik',
    content: (
      <>
        <p>
          Dinamik yaratilgan document exportlar, risk flaglari, moslik ballari
          va analitik procurement modellari yordamchi qaror vositalaridir. Ular
          davlat organi xulosasi, tender komissiyasi qarori, yuridik, soliq yoki
          moliyaviy maslahat hisoblanmaydi.
        </p>
        <p>
          AI natijasi noto‘liq, eskirgan yoki xato bo‘lishi mumkin. Foydalanuvchi
          eksport qilinadigan hujjat, hisob-kitob, citation va tender talablarini
          topshirishdan oldin mustaqil ravishda tekshirishi shart. Tender-Helper
          AI foydalanuvchining tekshirilmagan AI natijasiga tayangan qarori uchun
          qonun ruxsat bergan maksimal doirada javobgar bo‘lmaydi.
        </p>
      </>
    ),
  },
  {
    id: 'availability',
    title: '6. Xizmat mavjudligi va o‘zgarishlar',
    content: (
      <p>
        Davlat portallari, registry, Google, AI, email, SMS yoki cloud
        providerlaridagi uzilishlar ayrim funksiyalarni vaqtincha cheklashi
        mumkin. Platforma xavfsizlik, qonunchilik yoki mahsulot talabi sabab
        funksiyalar va tariflarni oldindan xabar berilgan holda o‘zgartirishi mumkin.
      </p>
    ),
  },
  {
    id: 'termination',
    title: '7. Bekor qilish va murojaatlar',
    content: (
      <p>
        Foydalanuvchi obunani amaldagi billing shartlari asosida bekor qilishi
        mumkin. Shartlar, hisob yoki korporativ kelishuv bo‘yicha savollar
        info@tenderhelperai.com manziliga yuboriladi.
      </p>
    ),
  },
];

export default function TermsPage() {
  return (
    <LegalPageLayout
      eyebrow="Legal · Terms of Service"
      title="Foydalanish shartlari"
      summary="Ushbu shartlar Tender-Helper AI hisoblari, obuna tariflari, jamoa vakolatlari va AI asosidagi tender xizmatlaridan foydalanish qoidalarini belgilaydi."
      lastUpdated="June 15, 2026"
      sections={sections}
    />
  );
}
