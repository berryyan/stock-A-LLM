# tests/test_embedding_model.py
"""
测试 BGE-M3 嵌入模型
"""

import sys
sys.path.append('.')

import numpy as np
import time
from models.embedding_model import get_embedding_model, encode_text, batch_encode_texts

def test_model_loading():
    """测试模型加载"""
    print("\n1. 测试模型加载...")
    
    try:
        start_time = time.time()
        model = get_embedding_model()
        load_time = time.time() - start_time
        
        print(f"   ✅ 模型加载成功")
        print(f"   加载时间: {load_time:.2f} 秒")
        print(f"   模型名称: {model.model_name}")
        print(f"   运行设备: {model.device_type}")
        print(f"   向量维度: {model.get_dimension()}")
        
        return True
    except Exception as e:
        print(f"   ❌ 模型加载失败: {e}")
        return False

def test_single_text_encoding():
    """测试单个文本编码"""
    print("\n2. 测试单个文本编码...")
    
    try:
        # 测试文本
        test_texts = [
            "平安银行发布2024年第一季度财报",
            "人工智能技术在金融领域的应用越来越广泛",
            "股票市场今日整体表现良好，沪深300指数上涨2.5%",
            "The stock market performed well today",  # 测试英文
            ""  # 测试空文本
        ]
        
        model = get_embedding_model()
        
        for text in test_texts:
            if text:
                print(f"\n   测试文本: '{text[:30]}...'")
            else:
                print(f"\n   测试文本: '[空文本]'")
                
            start_time = time.time()
            embedding = encode_text(text)
            encode_time = time.time() - start_time
            
            print(f"   向量形状: {embedding.shape}")
            print(f"   向量范数: {np.linalg.norm(embedding):.4f}")
            print(f"   编码时间: {encode_time*1000:.2f} ms")
            
            # 检查向量是否归一化
            if not text:
                print(f"   空文本处理: {'✅ 返回零向量' if np.allclose(embedding, 0) else '❌ 非零向量'}")
            else:
                is_normalized = np.abs(np.linalg.norm(embedding) - 1.0) < 0.01
                print(f"   归一化: {'✅' if is_normalized else '❌'}")
        
        return True
    except Exception as e:
        print(f"   ❌ 单文本编码失败: {e}")
        return False

def test_batch_encoding():
    """测试批量编码"""
    print("\n3. 测试批量编码...")
    
    try:
        # 准备批量文本
        texts = [
            "深度学习在自然语言处理中的应用",
            "股票投资需要关注公司基本面",
            "量化交易策略的优化方法",
            "ESG投资理念逐渐成为主流",
            "区块链技术在金融科技中的创新应用",
            "",  # 空文本
            "人工智能助力智慧金融发展"
        ] * 10  # 重复10次，共70个文本
        
        print(f"   批量大小: {len(texts)} 个文本")
        
        # 测试批量编码
        start_time = time.time()
        embeddings = batch_encode_texts(texts, batch_size=32, show_progress_bar=False)
        batch_time = time.time() - start_time
        
        print(f"   ✅ 批量编码成功")
        print(f"   返回向量数: {len(embeddings)}")
        print(f"   总时间: {batch_time:.2f} 秒")
        print(f"   平均时间: {batch_time/len(texts)*1000:.2f} ms/文本")
        
        # 检查结果
        valid_embeddings = [emb for emb in embeddings if not np.allclose(emb, 0)]
        print(f"   有效向量数: {len(valid_embeddings)}")
        
        return True
    except Exception as e:
        print(f"   ❌ 批量编码失败: {e}")
        return False

def test_similarity():
    """测试相似度计算"""
    print("\n4. 测试相似度计算...")
    
    try:
        model = get_embedding_model()
        
        # 测试相似文本
        text_pairs = [
            ("股票市场分析", "股票市场研究"),  # 高相似度
            ("人工智能技术", "AI技术应用"),      # 中等相似度
            ("股票投资策略", "天气预报信息"),    # 低相似度
            ("平安银行", "平安银行")            # 相同文本
        ]
        
        for text1, text2 in text_pairs:
            similarity = model.compute_similarity(text1, text2)
            print(f"\n   文本1: '{text1}'")
            print(f"   文本2: '{text2}'")
            print(f"   相似度: {similarity:.4f}")
        
        # 测试向量相似度
        vec1 = encode_text("金融科技创新")
        vec2 = encode_text("金融技术革新")
        vec_similarity = model.compute_similarity(vec1, vec2)
        print(f"\n   向量相似度测试: {vec_similarity:.4f}")
        
        return True
    except Exception as e:
        print(f"   ❌ 相似度计算失败: {e}")
        return False

def test_real_data():
    """测试真实数据编码"""
    print("\n5. 测试真实股票数据编码...")
    
    try:
        # 模拟真实的股票相关文本
        real_texts = [
            "平安银行（000001.SZ）2024年第一季度实现营业收入442.89亿元，同比增长2.8%；归属于本行股东的净利润142.52亿元，同比增长10.1%。",
            "投资者问：公司在人工智能领域有哪些布局？回答：公司高度重视人工智能技术的应用，已在智能客服、风险控制等多个领域取得积极进展。",
            "【资金流向】平安银行今日主力资金净流入2.3亿元，其中超大单净流入1.5亿元，显示机构资金看好。",
            "【公告】平安银行关于2024年年度权益分派实施公告：每10股派发现金红利3.18元（含税）。"
        ]
        
        embeddings = batch_encode_texts(real_texts)
        
        print(f"   ✅ 成功编码 {len(embeddings)} 个真实文本")
        
        # 计算文本之间的相似度矩阵
        print("\n   相似度矩阵:")
        print("   ", end="")
        for i in range(len(real_texts)):
            print(f"文本{i+1:2d}", end=" ")
        print()
        
        for i in range(len(real_texts)):
            print(f"   文本{i+1}", end=" ")
            for j in range(len(real_texts)):
                if i == j:
                    sim = 1.0
                else:
                    sim = np.dot(embeddings[i], embeddings[j])
                print(f"{sim:5.3f}", end=" ")
            print()
        
        return True
    except Exception as e:
        print(f"   ❌ 真实数据编码失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 BGE-M3 嵌入模型测试")
    print("=" * 70)
    
    # 运行所有测试
    tests = [
        ("模型加载", test_model_loading),
        ("单文本编码", test_single_text_encoding),
        ("批量编码", test_batch_encoding),
        ("相似度计算", test_similarity),
        ("真实数据", test_real_data)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*70}")
        print(f"测试: {test_name}")
        print('='*70)
        
        success = test_func()
        results.append((test_name, success))
    
    # 总结
    print("\n" + "=" * 70)
    print("测试总结")
    print("=" * 70)
    
    for test_name, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"{test_name}: {status}")
    
    all_passed = all(success for _, success in results)
    if all_passed:
        print("\n🎉 所有测试通过！嵌入模型已准备就绪。")
        print("\n下一步：实现文档处理模块 (rag/document_processor.py)")
    else:
        print("\n⚠️ 部分测试失败，请检查错误信息。")

if __name__ == "__main__":
    main()