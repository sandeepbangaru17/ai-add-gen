"""
AI Ad Creation Pipeline — Main Orchestrator
Runs all 8 stages sequentially to produce a complete video advertisement.

Usage:
    python pipeline.py                          # Interactive brief + full pipeline
    python pipeline.py --default                # Use ZunoSync test brief
    python pipeline.py --brief path/to/brief.json  # Use existing brief
    python pipeline.py --start-from 3           # Resume from Stage 3
    python pipeline.py --default --start-from 5 # Test from Stage 5
"""

import argparse
import json
import sys
import time
from pathlib import Path

# Fix Windows console encoding for Unicode characters
if sys.platform == "win32":
    import io

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# Ensure project root is in path
sys.path.insert(0, str(Path(__file__).parent))

from config import OUTPUT_DIR, ensure_dirs
from agents import brief_agent, script_agent, voice_agent, prompt_agent
from agents import video_agent, stitch_agent, post_agent, export_agent


STAGES = {
    1: ("Brief Input", "brief_agent"),
    2: ("Script Generation", "script_agent"),
    3: ("Voice Generation", "voice_agent"),
    4: ("Scene Prompt Creation", "prompt_agent"),
    5: ("AI Video Generation", "video_agent"),
    6: ("Asset Stitching", "stitch_agent"),
    7: ("Post-Processing", "post_agent"),
    8: ("Final Export", "export_agent"),
}


def print_banner():
    print("""
+==============================================================+
|                                                              |
|         ** AI AD CREATION PIPELINE  v1.0 **                  |
|                                                              |
|         Powered by Open-Source Tools:                        |
|         - Groq (Llama 3.3) -- Script & Prompts              |
|         - edge-tts -- Voice Generation                       |
|         - Hugging Face -- Image Generation                   |
|         - FFmpeg -- Video Processing                         |
|                                                              |
+==============================================================+
    """)


def run_pipeline(
    brief_path: str = None, use_default: bool = False, start_from: int = 1
):
    """Run the full pipeline from the specified starting stage."""
    print_banner()
    ensure_dirs()

    start_time = time.time()
    results = {}

    for stage_num in range(start_from, 9):
        stage_name, agent_name = STAGES[stage_num]
        agent_func = globals()[agent_name]

        print(f"\n{'━' * 60}")
        print(f"  ▶ STAGE {stage_num}/8: {stage_name}")
        print(f"{'━' * 60}")

        stage_start = time.time()

        try:
            if stage_num == 1:
                result = agent_func(
                    brief_path=brief_path,
                    use_default=use_default,
                )
            else:
                result = agent_func()

            stage_duration = time.time() - stage_start
            results[f"stage_{stage_num}"] = {
                "name": stage_name,
                "status": "completed",
                "duration_seconds": round(stage_duration, 1),
                "result": result,
            }
            print(f"\n   ⏱  Stage {stage_num} completed in {stage_duration:.1f}s")

        except Exception as e:
            stage_duration = time.time() - stage_start
            results[f"stage_{stage_num}"] = {
                "name": stage_name,
                "status": "failed",
                "error": str(e),
                "duration_seconds": round(stage_duration, 1),
            }
            print(f"\n   ❌ Stage {stage_num} FAILED: {e}")
            print(
                f"\n   💡 Fix the issue and re-run with: python pipeline.py --start-from {stage_num}"
            )
            break

    # Final summary
    total_time = time.time() - start_time
    print(f"\n{'═' * 60}")
    print(f"  📊  PIPELINE SUMMARY")
    print(f"{'═' * 60}")
    print(f"  Total time: {total_time:.1f}s ({total_time / 60:.1f} min)")
    print()

    for key, val in results.items():
        status = "✅" if val["status"] == "completed" else "❌"
        print(f"  {status} {val['name']}: {val['status']} ({val['duration_seconds']}s)")

    # Save results
    results_path = OUTPUT_DIR / "pipeline_results.json"
    with open(results_path, "w", encoding="utf-8") as f:
        # Remove non-serializable result data
        clean = {}
        for k, v in results.items():
            clean[k] = {kk: vv for kk, vv in v.items() if kk != "result"}
        json.dump(clean, f, indent=2)

    print(f"\n  📄 Results saved: {results_path}")
    return results


def main():
    parser = argparse.ArgumentParser(
        description="AI Ad Creation Pipeline — Generate video ads end-to-end",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python pipeline.py --default              Use ZunoSync test brief
  python pipeline.py --brief my_brief.json  Use custom brief
  python pipeline.py --start-from 5         Resume from Stage 5
        """,
    )
    parser.add_argument("--brief", type=str, help="Path to existing brief.json")
    parser.add_argument(
        "--default", action="store_true", help="Use the default ZunoSync test brief"
    )
    parser.add_argument(
        "--start-from",
        type=int,
        default=1,
        choices=range(1, 9),
        help="Start from a specific stage (1-8)",
    )

    args = parser.parse_args()

    if args.brief and args.default:
        print("❌ Cannot specify both --brief and --default")
        sys.exit(1)

    run_pipeline(
        brief_path=args.brief,
        use_default=args.default,
        start_from=args.start_from,
    )


if __name__ == "__main__":
    main()
