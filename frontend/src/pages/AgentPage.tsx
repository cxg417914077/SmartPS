import { useState, ChangeEvent, FormEvent } from 'react';
// 假设您的 config 文件仍然在正确的位置
import { API_BASE_URL } from '../config';

// 为日志窗口定义一个类型接口
// 注意：由于新接口不返回思考和观察步骤，我们主要用它来显示最终结果或错误信息
interface AgentStep {
  type: 'final_output' | 'error' | 'info';
  content: string;
}

export function AgentPage(): JSX.Element {
  const [prompt, setPrompt] = useState<string>('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [inputImageUrl, setInputImageUrl] = useState<string | null>(null);
  const [outputImageUrl, setOutputImageUrl] = useState<string | null>(null);

  const [isLoading, setIsLoading] = useState<boolean>(false);
  // steps 现在用于显示状态信息，而不是详细的 Agent 步骤
  const [steps, setSteps] = useState<AgentStep[]>([]);

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>): void => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setSelectedFile(file);
      // 清理旧的 URL 对象以避免内存泄漏
      if (inputImageUrl) {
        URL.revokeObjectURL(inputImageUrl);
      }
      const newImageUrl = URL.createObjectURL(file);
      setInputImageUrl(newImageUrl);
      // 重置输出图片和日志
      setOutputImageUrl(null);
      setSteps([]);
    }
  };

  const handleSubmit = async (e: FormEvent<HTMLFormElement>): Promise<void> => {
    e.preventDefault();
    if (isLoading || !selectedFile || !prompt) {
      alert("请输入指令并选择一张图片。");
      return;
    }

    setIsLoading(true);
    setSteps([{ type: 'info', content: '智能体已启动，正在处理图片...' }]); // 提供初始状态
    setOutputImageUrl(null);

    const formData = new FormData();
    formData.append('prompt', prompt);
    formData.append('file', selectedFile);

    try {
      // API 请求地址保持不变
      const response = await fetch(`${API_BASE_URL}/agent/image_process`, {
        method: 'POST',
        body: formData,
        // 如果需要，请取消注释 headers
        // headers: {
        //   'Authorization': `Bearer ${localStorage.getItem('authToken')}`
        // }
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`服务器错误: ${response.status} ${errorText}`);
      }

      // **核心修改：直接解析 JSON 响应，而不是读取流**
      const data: { image: string } = await response.json();

      if (data && data.image) {
        // 从选择的文件中获取正确的 MIME 类型
        const imageFormat = selectedFile.type;
        const imageUrl = `data:${imageFormat};base64,${data.image}`;
        setOutputImageUrl(imageUrl);
        setSteps(prevSteps => [...prevSteps, { type: 'final_output', content: '图片处理成功！' }]);
      } else {
        throw new Error("从服务器返回的数据格式不正确。");
      }

    } catch (error) {
      console.error("请求失败:", error);
      const errorMessage = error instanceof Error ? error.message : '连接服务器或处理请求失败。';
      setSteps(prevSteps => [...prevSteps, { type: 'error', content: errorMessage }]);
    } finally {
      setIsLoading(false);
    }
  };

  // renderStep 函数简化，因为它不再需要处理 'thought' 和 'observation'
  const renderStep = (step: AgentStep, index: number): JSX.Element => {
    switch (step.type) {
      case 'info':
        return <div key={index} className="step info"><strong>ℹ️ 状态:</strong> {step.content}</div>;
      case 'final_output':
        return <div key={index} className="step final"><strong>✅ 结果:</strong> {step.content}</div>;
      case 'error':
        return <div key={index} className="step error"><strong>❌ 错误:</strong> {step.content}</div>;
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
          {steps.map(renderStep)}
          {/* 这里不再需要单独的 loading 状态，因为它已被整合到 steps 中 */}
        </div>

        <form onSubmit={handleSubmit} className="input-form">
          <input type="file" onChange={handleFileChange} accept="image/*" disabled={isLoading} />
          <input
            type="text"
            value={prompt}
            onChange={(e: ChangeeEvent<HTMLInputElement>) => setPrompt(e.target.value)}
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