/* 请用以下完整内容替换该文件的所有内容 */

import { useState, ChangeEvent, FormEvent } from 'react';
import { API_BASE_URL } from '../config'; // 1. 导入基础 URL

// 为 SSE 流返回的步骤数据定义一个类型接口
interface AgentStep {
  type: 'thought' | 'observation' | 'final_output' | 'error' | 'final_image';
  content: string;
  format?: string;
}

export function AgentPage(): JSX.Element {
  const [prompt, setPrompt] = useState<string>('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [inputImageUrl, setInputImageUrl] = useState<string | null>(null);
  const [outputImageUrl, setOutputImageUrl] = useState<string | null>(null);

  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [steps, setSteps] = useState<AgentStep[]>([]);

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>): void => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setSelectedFile(file);
      if (inputImageUrl) {
        URL.revokeObjectURL(inputImageUrl);
      }
      const newImageUrl = URL.createObjectURL(file);
      setInputImageUrl(newImageUrl);
      setOutputImageUrl(null);
    }
  };

  const handleSubmit = async (e: FormEvent<HTMLFormElement>): Promise<void> => {
    e.preventDefault();
    if (isLoading || !selectedFile || !prompt) {
      alert("请输入指令并选择一张图片。");
      return;
    }

    setIsLoading(true);
    setSteps([]);
    setOutputImageUrl(null);

    const formData = new FormData();
    formData.append('prompt', prompt);
    formData.append('file', selectedFile);

    try {
      // 2. 更新 fetch 请求地址
      const response = await fetch(`${API_BASE_URL}/agent/image_process`, {
        method: 'POST',
        body: formData,
        // 如果你的 agent 接口需要认证，你需要在这里添加 Authorization 头
        // headers: {
        //   'Authorization': `Bearer ${localStorage.getItem('authToken')}`
        // }
      });

      if (!response.body) {
        throw new Error("Response body is null");
      }

      const reader = response.body.pipeThrough(new TextDecoderStream()).getReader();

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        const lines = value.split('\n\n').filter(line => line.trim() !== '');
        for (const line of lines) {
          if (line.startsWith('data:')) {
            try {
              const jsonString = line.substring(5);
              const data: AgentStep = JSON.parse(jsonString);

              if (data.type === 'end') {
                setIsLoading(false);
                return;
              } else if (data.type === 'final_image' && data.format) {
                const imageUrl = `data:${data.format};base64,${data.content}`;
                setOutputImageUrl(imageUrl);
              } else {
                setSteps(prevSteps => [...prevSteps, data]);
              }
            } catch (parseError) {
              console.error("解析 SSE 数据块失败:", parseError, "原始数据:", line);
            }
          }
        }
      }
    } catch (error) {
      console.error("请求流错误:", error);
      setSteps(prevSteps => [...prevSteps, { type: 'error', content: '连接服务器或处理请求失败。' }]);
    } finally {
      setIsLoading(false);
    }
  };

  const renderStep = (step: AgentStep, index: number): JSX.Element | null => {
    switch (step.type) {
      case 'thought':
        return <div key={index} className="step thought"><strong>🤔 思考:</strong> <pre>{step.content}</pre></div>;
      case 'observation':
        return <div key={index} className="step observation"><strong>👀 观察:</strong> <pre>{step.content}</pre></div>;
      case 'final_output':
        return <div key={index} className="step final"><strong>✅ 最终答案:</strong> {step.content}</div>;
      case 'error':
        return <div key={index} className="step error"><strong>❌ 错误:</strong> {step.content}</div>;
      default:
        return null;
    }
  };

  return (
    <div className="agent-page-container">
      <main>
        <div className="image-io">
          <div className="image-container">
            <h3 className="image-container-title">输入图片</h3>
            {inputImageUrl ?
              <img src={inputImageUrl} alt="输入图片预览" /> :
              <p className="image-container-placeholder">请选择一张图片进行预览</p>
            }
          </div>
          <div className="image-container">
            <h3 className="image-container-title">输出图片</h3>
            {outputImageUrl ?
              <img src={outputImageUrl} alt="处理结果" /> :
              <p className="image-container-placeholder">处理后的图片将显示在这里</p>
            }
          </div>
        </div>

        <div className="log-window">
          {steps.filter(step => step.type !== 'final_image').map(renderStep)}
          {isLoading && <div className="step loading">智能体正在工作中...</div>}
        </div>

        <form onSubmit={handleSubmit} className="input-form">
          <input type="file" onChange={handleFileChange} accept="image/*" disabled={isLoading} />
          <input
            type="text"
            value={prompt}
            onChange={(e: ChangeEvent<HTMLInputElement>) => setPrompt(e.target.value)}
            placeholder="您想对图片做什么？"
            disabled={isLoading}
          />
          <button type="submit" disabled={isLoading || !selectedFile}>
            {isLoading ? '处理中...' : '运行智能体'}
          </button>
        </form>
      </main>
    </div>
  );
}