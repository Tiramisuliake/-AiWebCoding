"""
web-admin CI 脚本
运行：python scripts/run_ci.py
成功：退出码 0
失败：退出码 1

包含检查：
1. 黄金原则（golden_rules.py）— 文件大小、密钥、console.log、文档新鲜度
2. pytest（后端测试）— 由 backend-dev 配置后激活

用法：
  python scripts/run_ci.py           # 运行所有检查
  python scripts/run_ci.py --quick   # 只跑黄金原则
"""
import sys
import subprocess
from pathlib import Path

# 项目根目录
ROOT = Path(__file__).parent.parent

def run_golden_rules():
    """运行黄金原则检查"""
    print("=" * 60)
    print(">> 黄金原则检查（golden_rules.py）")
    print("=" * 60)

    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "golden_rules", ROOT / "scripts" / "golden_rules.py"
    )
    gr = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gr)

    # 检查源代码目录（backend-dev 创建后自动生效）
    src_dirs = []
    if (ROOT / "backend").exists():
        src_dirs.append(str(ROOT / "backend"))
    if (ROOT / "frontend" / "src").exists():
        src_dirs.append(str(ROOT / "frontend" / "src"))

    if not src_dirs:
        print("[SKIP] 源代码目录尚未创建，跳过黄金原则检查")
        return 0, 0, 0

    docs_dir = str(ROOT / ".plans" / "web-admin" / "docs")
    failures, warnings, infos = gr.check_all(src_dirs, docs_dir=docs_dir)
    return failures, warnings, infos


def run_pytest():
    """运行 pytest 后端测试"""
    backend_tests = ROOT / "backend" / "tests"
    if not backend_tests.exists():
        print("\n[SKIP] backend/tests/ 尚未创建，跳过 pytest")
        return 0

    print("\n" + "=" * 60)
    print(">> pytest 后端测试")
    print("=" * 60)

    result = subprocess.run(
        [sys.executable, "-m", "pytest", str(backend_tests), "-v", "--tb=short"],
        cwd=ROOT / "backend"
    )
    return result.returncode


def main():
    quick = "--quick" in sys.argv

    # 1. 黄金原则
    failures, warnings, _ = run_golden_rules()

    # 2. pytest（非 quick 模式）
    pytest_code = 0
    if not quick:
        pytest_code = run_pytest()

    # 汇总
    print("\n" + "=" * 60)
    print("CI 结果汇总")
    print("=" * 60)
    print(f"  黄金原则 — 失败: {failures}, 警告: {warnings}")
    if not quick:
        print(f"  pytest    — {'PASS' if pytest_code == 0 else 'FAIL'}")

    if failures > 0 or pytest_code != 0:
        print("\n[FAIL] CI 失败 — 请修复上述问题后再提交审查")
        sys.exit(1)
    else:
        print("\n[PASS] CI 通过")
        sys.exit(0)


if __name__ == "__main__":
    main()
