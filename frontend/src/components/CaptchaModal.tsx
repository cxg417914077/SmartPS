/* 请将以下完整内容创建并保存到该文件中 */

import ReCAPTCHA from 'react-google-recaptcha';
import './CaptchaModal.css'; // 我们稍后会创建这个文件

interface CaptchaModalProps {
  isOpen: boolean;
  onClose: () => void;
  onVerify: (token: string) => void;
  siteKey: string;
}

export function CaptchaModal({ isOpen, onClose, onVerify, siteKey }: CaptchaModalProps) {
  if (!isOpen) {
    return null;
  }

  const handleCaptchaChange = (token: string | null) => {
    if (token) {
      onVerify(token);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <h4>请完成人机验证</h4>
        <ReCAPTCHA
          sitekey={siteKey}
          onChange={handleCaptchaChange}
        />
        <button onClick={onClose} className="close-btn">关闭</button>
      </div>
    </div>
  );
}