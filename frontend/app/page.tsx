import { ArrowRight, LockKeyhole, MessageSquareText, ShieldCheck } from 'lucide-react';
import Link from 'next/link';

import Button from '@/components/common/Button';

export default function HomePage() {
  return (
    <div className="mx-auto flex w-full max-w-7xl flex-col gap-12 px-4 py-10 sm:px-6 lg:px-8">
      <section className="grid gap-8 lg:grid-cols-[1.1fr_0.9fr] lg:items-center">
        <div className="space-y-6">
          <div className="inline-flex items-center gap-2 rounded-full border border-rose-200 bg-white px-3 py-1 text-sm font-medium text-rose-700">
            <ShieldCheck className="h-4 w-4" aria-hidden="true" />
            Phân tích tham khảo, ưu tiên quyền riêng tư
          </div>
          <div className="space-y-4">
            <h1 className="max-w-3xl text-4xl font-bold leading-tight text-slate-950 sm:text-5xl">
              Love Emotion
            </h1>
            <p className="max-w-2xl text-lg leading-8 text-slate-600">
              Web app hỗ trợ đọc sắc thái cảm xúc trong đoạn hội thoại tình cảm và gợi ý cách phản hồi
              nhẹ nhàng, không thao túng và không kết luận chắc chắn về người khác.
            </p>
          </div>
          <Link href="/analyze">
            <Button>
              Bắt đầu phân tích
              <ArrowRight className="h-4 w-4" aria-hidden="true" />
            </Button>
          </Link>
        </div>

        <div className="rounded-lg border border-rose-100 bg-white p-5 shadow-sm">
          <div className="space-y-4">
            <div className="rounded-lg bg-rose-50 p-4">
              <p className="text-sm font-semibold text-slate-950">Đầu vào mẫu</p>
              <p className="mt-2 whitespace-pre-line text-sm leading-6 text-slate-600">
                Em sao vậy?{'\n'}Không sao.{'\n'}Anh thấy em hơi lạ.{'\n'}Em mệt thôi.
              </p>
            </div>
            <div className="rounded-lg bg-teal-50 p-4">
              <p className="text-sm font-semibold text-slate-950">Gợi ý phản hồi</p>
              <p className="mt-2 text-sm leading-6 text-slate-700">
                Anh hiểu rồi, em nghỉ một chút nha. Khi nào em muốn nói thì anh vẫn ở đây nghe em.
              </p>
            </div>
          </div>
        </div>
      </section>

      <section className="grid gap-4 md:grid-cols-3">
        <div className="rounded-lg border border-rose-100 bg-white p-5">
          <MessageSquareText className="mb-4 h-6 w-6 text-rose-600" aria-hidden="true" />
          <h2 className="font-semibold text-slate-950">Nhập thủ công</h2>
          <p className="mt-2 text-sm leading-6 text-slate-600">
            Không đọc trộm tin nhắn, thông báo, danh bạ hoặc tài khoản cá nhân.
          </p>
        </div>
        <div className="rounded-lg border border-rose-100 bg-white p-5">
          <LockKeyhole className="mb-4 h-6 w-6 text-teal-600" aria-hidden="true" />
          <h2 className="font-semibold text-slate-950">Không lưu mặc định</h2>
          <p className="mt-2 text-sm leading-6 text-slate-600">
            MVP chỉ gửi dữ liệu đến backend local để trả kết quả mock, chưa có database lịch sử.
          </p>
        </div>
        <div className="rounded-lg border border-rose-100 bg-white p-5">
          <ShieldCheck className="mb-4 h-6 w-6 text-amber-600" aria-hidden="true" />
          <h2 className="font-semibold text-slate-950">Có cảnh báo rõ ràng</h2>
          <p className="mt-2 text-sm leading-6 text-slate-600">
            Kết quả chỉ mang tính tham khảo và không thay thế giao tiếp trực tiếp.
          </p>
        </div>
      </section>
    </div>
  );
}
