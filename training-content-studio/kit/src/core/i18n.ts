// The few fixed UI strings the kit draws itself (everything else comes from template props).
import { useLayout } from './ctx';

const EN = {
  quick_check: 'Quick check', definition: 'Definition', takeaways: 'Key takeaways', dont: "Don't", do: 'Do',
  inbox: 'Inbox', to: 'To', external: 'This message came from outside your organization.', approve_q: 'Approve sign-in?',
  deny: 'Deny', approve: 'Approve', sign_in: 'Sign in', email: 'Email', password: 'Password', your_choice: 'What would you do?',
  chosen: 'Chosen', search: 'Search', save: 'Save', type_message: 'Type a message', now: 'now', step: 'Step',
};
type Dict = typeof EN;
const AR: Dict = {
  quick_check: 'سؤال سريع', definition: 'تعريف', takeaways: 'أهم النقاط', dont: 'لا تفعل', do: 'افعل',
  inbox: 'البريد الوارد', to: 'إلى', external: 'هذه الرسالة من خارج مؤسستك.', approve_q: 'الموافقة على تسجيل الدخول؟',
  deny: 'رفض', approve: 'موافقة', sign_in: 'تسجيل الدخول', email: 'البريد الإلكتروني', password: 'كلمة المرور', your_choice: 'ماذا ستفعل؟',
  chosen: 'الاختيار', search: 'بحث', save: 'حفظ', type_message: 'اكتب رسالة', now: 'الآن', step: 'خطوة',
};

export const useT = () => {
  const { lang } = useLayout();
  const d = lang.startsWith('ar') ? AR : EN;
  return (k: keyof Dict) => d[k];
};
