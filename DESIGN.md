# CodeSense AI Frontend Design Guide

> **Ghi chú chuyển hướng (Pivot Note - APT-002):** Hướng dẫn thiết kế giao diện cho **CodeSense AI** - *Adaptive Programming Tutor for Beginner C# OOP Students*. Kế thừa nền tảng hệ thống thiết kế frontend từ Love Sense AI.

## 1. Brand Direction

**App name:** CodeSense AI (Research: Adaptive Programming Tutor for Beginner C# OOP Students)

Love Sense AI is a web app that helps users analyze the emotional tone of romantic conversations they manually enter. The app provides gentle response suggestions and keeps privacy as a core product value.

The product must never feel like a tool for monitoring, controlling, or secretly reading another person. It should not imply that it can know what someone truly thinks or feels. Every result is an interpretation aid, not a final judgment.

**Brand tone:**

- Private and respectful
- Warm but not childish
- Modern and calm
- Trustworthy and careful with user data
- Supportive without being manipulative

**Core promise:**

Love Sense AI helps users slow down, understand possible conversation signals, and respond more gently while keeping data control visible.

## 2. Design Inspiration

The visual direction may take broad inspiration from strong product interfaces, but must not copy any brand, layout, asset, or trademarked style directly.

- **Vercel:** clean layouts, precise typography, minimal spacing system, direct product hierarchy.
- **Linear:** focused dashboards, clear active states, refined cards, strong keyboard and focus behavior.
- **Supabase:** developer-trust feeling, clear data and privacy language, structured settings screens.
- **Stripe:** soft gradients, premium visual hierarchy, polished CTA and information grouping.
- **Notion:** readable content, friendly forms, approachable empty states.
- **Apple:** generous white space, calm surfaces, restrained premium feel.

The combined direction is: **warm privacy-first AI companion dashboard**, not a dating tracker and not a surveillance product.

## 3. Visual System

### Color

Use a warm, soft palette with enough contrast for real app usage.

- **Background:** warm off-white, soft rose tint, and slate text contrast.
- **Primary:** rose, pink, or warm red for main actions and brand anchors.
- **Accent:** teal or emerald for safe, saved, neutral-positive, or privacy-confirmed states.
- **Danger:** clear red for destructive actions, but avoid harsh full-page danger styling.
- **Border:** `rose-100`, `rose-200`, `slate-100`, `slate-200`.
- **Text:** `slate-950` for main headings, `slate-700` for important body copy, `slate-500` for supporting text.

### Surfaces

- Main page background should feel warm and calm, not flat gray.
- Cards should use white or near-white backgrounds with subtle border and shadow.
- Avoid heavy glassmorphism, strong neon gradients, or noisy decorative shapes.
- Hero areas can use soft rose/white gradients or light blur effects when they support readability.

### Radius

- Main cards: `rounded-2xl`
- Inputs and buttons: `rounded-xl`
- Badges and small pills: `rounded-full` or `rounded-xl`
- Avoid inconsistent radius values unless a component has a clear reason.

### Shadow

Use shadows sparingly.

- Prefer soft, subtle shadows for cards and elevated panels.
- Do not stack heavy shadows.
- Hover elevation should be small and predictable.

## 4. Typography

Typography should feel modern, readable, and direct.

- Headings are strong, clear, and compact.
- Body text is easy to scan, especially in forms and result panels.
- Vietnamese copy should be short, friendly, and privacy-safe.
- Avoid oversized text inside dashboards, sidebars, and compact panels.
- Do not use negative letter spacing.

### Copywriting Rules

Avoid phrases that imply surveillance or certainty:

- "biết người yêu nghĩ gì"
- "theo dõi người yêu"
- "kiểm tra người yêu"
- "dự đoán chắc chắn cảm xúc"
- "phát hiện người yêu phản bội"

Prefer phrases that describe the product accurately:

- "phân tích sắc thái hội thoại"
- "gợi ý phản hồi nhẹ nhàng"
- "kết quả chỉ mang tính tham khảo"
- "không lưu nội dung chat nếu bạn chưa đồng ý"
- "không đọc trộm tin nhắn"
- "ưu tiên quyền riêng tư"

Every analysis result should preserve the warning that the output is only a reference and cannot replace direct communication.

## 5. Page Patterns

### Landing Page `/`

The landing page should immediately explain what Love Sense AI does and what it does not do.

Required pattern:

- Large hero section with app name and clear value proposition.
- Primary CTA: "Bắt đầu phân tích".
- Secondary link to privacy or data control.
- Feature cards:
  - Manual input only, no secret message reading.
  - Chat content is not saved unless the user agrees.
  - Gentle response suggestions.
  - Clear data deletion controls.
- 3-step flow:
  1. Nhập đoạn chat
  2. Thêm bối cảnh cá nhân hóa
  3. Nhận phân tích và gợi ý phản hồi

The landing page should not make claims that the app can reveal what another person truly thinks.

### Analyze Page `/analyze`

This is the primary product screen and should receive the most design attention.

Desktop layout:

- Two columns.
- Left column: input form.
- Right column: result panel.
- Keep the form stable while result states change.

Mobile layout:

- Stack form first, result second.
- Buttons must be easy to tap.
- Textareas must not overflow the viewport.

Input form must include:

- Large textarea for the chat text.
- Textarea for personalization context.
- Checkbox to save analysis result.
- Checkbox to save original chat content.
- Privacy note explaining that chat content is not saved by default.
- Clear submit button.

Result panel states:

- Empty state before analysis.
- Loading state while analyzing.
- Friendly error state if the API fails.
- Result state with:
  - Overall emotion
  - Confidence
  - Emotion distribution
  - Summary
  - Context note
  - Suggested reply
  - Safety warning

### Auth Page `/auth`

The auth page should feel simple and secure.

Required pattern:

- Clear mode switch between login and registration.
- Email and password fields with labels.
- Visible loading state.
- Clear error state.
- Privacy note explaining that account data is used to scope profile, history, and consent.
- Mobile-friendly single-column layout.

### Profile Page `/profile`

The profile page should group related data so it feels optional and respectful.

Required sections:

- Hồ sơ của bạn
- Hồ sơ người ấy
- Phong cách giao tiếp
- Ghi chú riêng và dữ liệu tùy chọn

Rules:

- Use responsive grid cards.
- Labels must be clear.
- Sensitive or optional fields must not feel required.
- Height, weight, and appearance may exist as optional context but must not be used to infer emotions.
- Save and delete actions must be visually distinct.

### History Page `/history`

History should feel like a private archive, not a monitoring log.

Required pattern:

- Search or filter field when practical.
- List cards for analysis sessions.
- Detail panel for selected item.
- Empty state when there is no history.
- Loading and error states.
- Per-item delete action with confirmation.

Each item should show:

- Analysis time
- Overall emotion
- Confidence
- Short summary
- Whether original chat content was saved

Original chat content must only appear when `save_input=true` was accepted for that analysis.

### Privacy Page `/privacy`

Privacy should be presented as a control center.

Required pattern:

- Explain what data may be saved.
- Explain what is not saved by default.
- Show consent settings clearly.
- Provide destructive actions:
  - Delete analysis history
  - Delete personalization profile
  - Delete all user data
- Every destructive action must ask for confirmation.

Danger styling should be clear but not visually aggressive.

## 6. Motion Guidelines

Motion should support clarity, not distract from sensitive content.

- Use transitions between `150ms` and `300ms`.
- Hover states can slightly lift cards or soften borders.
- Loading can use skeletons, spinners, or soft pulse effects.
- Avoid looping decorative animations.
- Avoid motion that makes forms or result panels jump.
- Hero sections can use subtle gradient or blur backgrounds.
- Respect performance on low-end mobile devices.

## 7. Accessibility

Accessibility is part of the design system, not an afterthought.

Required baseline:

- Every input has a visible label.
- Buttons have visible text or an appropriate `aria-label`.
- Focus rings are visible on keyboard navigation.
- Alerts use semantic roles when appropriate, such as `role="alert"` for errors.
- Loading states use understandable text and may use `role="status"`.
- Mobile menu can be opened, closed, and navigated with a keyboard.
- Text contrast must be high enough on rose, teal, amber, and red surfaces.
- Do not rely on color alone to communicate destructive, success, or warning states.

## 8. Implementation Rules

These rules protect product safety and existing functionality.

- Do not edit backend code for UI-only work unless the task requires it.
- Do not break existing flows:
  - `/auth`
  - `/analyze`
  - `/profile`
  - `/history`
  - `/privacy`
- Do not change API contracts unless a backend task explicitly requires it.
- Do not commit `.env`, `.env.local`, API keys, tokens, or secrets.
- Do not hard-code production domains.
- Do not add `console.log` for `chat_text`, API keys, tokens, or sensitive user data.
- Do not save `chat_text` by default.
- Only save `chat_text` when the user explicitly consents with `save_input=true`.
- Keep privacy copy visible near any save option.
- Preserve user-owned data boundaries. Profile, history, and consent data must remain scoped by `user_id`.
- Prefer existing components before adding new dependencies.
- Use Tailwind classes consistently with the current component system.
- Update tests when UI text, labels, or states change.

## 9. Review Checklist for Future UI Work

Before merging frontend UI changes, verify:

- The page works on mobile, tablet, and desktop widths.
- Navigation active state is correct.
- Forms keep user input after validation or API errors.
- Loading, empty, success, and error states are visible and understandable.
- Delete actions have confirmation.
- Privacy and consent wording is not hidden.
- No sensitive data is logged.
- `npm run test`, `npm run typecheck`, `npm run build`, and `npm audit` have been run when the change affects frontend behavior.

