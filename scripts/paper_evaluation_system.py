"""
Comprehensive Evaluation System for Bangladesh Constitution Chatbot Paper
Addresses all reviewer comments with detailed metrics, confusion matrices, and visualizations
"""

import os
import sys
import json
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import List, Dict, Tuple, Optional
from collections import defaultdict, Counter
from datetime import datetime
import re
from sklearn.metrics import (
    confusion_matrix, 
    precision_recall_curve, 
    average_precision_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report
)

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.config import Config
from src.chatbot import ConstitutionChatbot


class PaperEvaluationSystem:
    """Complete evaluation system for paper metrics and analysis"""
    
    def __init__(self, output_dir: str = "paper/paper_evaluation_results"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(os.path.join(output_dir, "figures"), exist_ok=True)
        os.makedirs(os.path.join(output_dir, "tables"), exist_ok=True)
        os.makedirs(os.path.join(output_dir, "data"), exist_ok=True)
        
        self.config = Config()
        self.chatbot = None
        self.results = {
            "latency": [],
            "language_predictions": [],
            "language_ground_truth": [],
            "scope_predictions": [],
            "scope_ground_truth": [],
            "retrieval_scores": [],
            "retrieval_relevance": []
        }
        
    def initialize_chatbot(self):
        """Initialize the chatbot system"""
        print("🔧 Initializing chatbot for evaluation...")
        self.chatbot = ConstitutionChatbot(self.config)
        if not self.chatbot.is_ready():
            print("⚠️ Warning: Chatbot not fully initialized")
        else:
            print("✅ Chatbot ready for evaluation")
    
    # ==================== REVIEWER COMMENT 1: Latency Distribution ====================
    
    def measure_latency_distribution(self, test_queries: List[Dict], batch_size: int = 1):
        """
        Measure latency distribution with mean, median, p95
        
        Args:
            test_queries: List of {'query': str, 'use_llm': bool, 'language': str}
            batch_size: Number of queries per batch (1 for sequential)
        """
        print(f"\n{'='*80}")
        print("📊 LATENCY DISTRIBUTION ANALYSIS")
        print(f"{'='*80}\n")
        
        latencies = {
            'gemini': [],
            'local': [],
            'simple': []
        }
        
        for i, query_config in enumerate(test_queries, 1):
            print(f"Processing query {i}/{len(test_queries)}: {query_config['query'][:50]}...")
            
            # Measure latency
            start_time = time.time()
            result = self.chatbot.process_query(
                query=query_config['query'],
                use_llm=query_config.get('use_llm', True)
            )
            end_time = time.time()
            
            latency = end_time - start_time
            
            # Categorize by model type used
            if 'gemini' in str(result.get('answer', '')).lower() or result.get('processing_time', 0) > 3:
                model_type = 'gemini'
            elif result.get('processing_time', 0) < 1:
                model_type = 'simple'
            else:
                model_type = 'local'
            
            latencies[model_type].append(latency)
            self.results['latency'].append({
                'query': query_config['query'],
                'latency': latency,
                'model_type': model_type,
                'batch_size': batch_size,
                'use_llm': query_config.get('use_llm', True)
            })
        
        # Calculate statistics for each model type
        stats = {}
        for model_type, lats in latencies.items():
            if lats:
                stats[model_type] = {
                    'count': len(lats),
                    'mean': np.mean(lats),
                    'median': np.median(lats),
                    'p95': np.percentile(lats, 95),
                    'p99': np.percentile(lats, 99),
                    'std': np.std(lats),
                    'min': np.min(lats),
                    'max': np.max(lats)
                }
        
        # Overall statistics
        all_latencies = [item['latency'] for item in self.results['latency']]
        overall_stats = {
            'count': len(all_latencies),
            'mean': np.mean(all_latencies),
            'median': np.median(all_latencies),
            'p95': np.percentile(all_latencies, 95),
            'p99': np.percentile(all_latencies, 99),
            'std': np.std(all_latencies),
            'min': np.min(all_latencies),
            'max': np.max(all_latencies)
        }
        
        # Print results
        print(f"\n📈 Overall Latency Statistics (n={overall_stats['count']}):")
        print(f"  Mean:   {overall_stats['mean']:.3f}s")
        print(f"  Median: {overall_stats['median']:.3f}s")
        print(f"  P95:    {overall_stats['p95']:.3f}s")
        print(f"  P99:    {overall_stats['p99']:.3f}s")
        print(f"  Std:    {overall_stats['std']:.3f}s")
        print(f"  Min:    {overall_stats['min']:.3f}s")
        print(f"  Max:    {overall_stats['max']:.3f}s")
        
        print(f"\n📊 Per-Model Latency Statistics:")
        for model_type, model_stats in stats.items():
            if model_stats['count'] > 0:
                print(f"\n  {model_type.upper()} (n={model_stats['count']}):")
                print(f"    Mean:   {model_stats['mean']:.3f}s")
                print(f"    Median: {model_stats['median']:.3f}s")
                print(f"    P95:    {model_stats['p95']:.3f}s")
        
        # Create visualization
        self._plot_latency_distribution(latencies, overall_stats)
        
        # Save to CSV
        df = pd.DataFrame(self.results['latency'])
        df.to_csv(os.path.join(self.output_dir, "tables", "latency_distribution.csv"), index=False)
        
        # Save LaTeX table
        self._generate_latency_table(overall_stats, stats)
        
        return overall_stats, stats
    
    def _plot_latency_distribution(self, latencies: Dict, overall_stats: Dict):
        """Create latency distribution plots"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        # Plot 1: Histogram with statistics
        all_lats = [item['latency'] for item in self.results['latency']]
        axes[0, 0].hist(all_lats, bins=30, edgecolor='black', alpha=0.7)
        axes[0, 0].axvline(overall_stats['mean'], color='r', linestyle='--', linewidth=2, label=f'Mean: {overall_stats["mean"]:.3f}s')
        axes[0, 0].axvline(overall_stats['median'], color='g', linestyle='--', linewidth=2, label=f'Median: {overall_stats["median"]:.3f}s')
        axes[0, 0].axvline(overall_stats['p95'], color='orange', linestyle='--', linewidth=2, label=f'P95: {overall_stats["p95"]:.3f}s')
        axes[0, 0].set_xlabel('Latency (seconds)', fontsize=12)
        axes[0, 0].set_ylabel('Frequency', fontsize=12)
        axes[0, 0].set_title('Overall Latency Distribution', fontsize=14, fontweight='bold')
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)
        
        # Plot 2: Box plot by model type
        model_data = []
        model_labels = []
        for model_type, lats in latencies.items():
            if lats:
                model_data.append(lats)
                model_labels.append(model_type.capitalize())
        
        if model_data:
            axes[0, 1].boxplot(model_data, labels=model_labels)
            axes[0, 1].set_ylabel('Latency (seconds)', fontsize=12)
            axes[0, 1].set_title('Latency by Model Type', fontsize=14, fontweight='bold')
            axes[0, 1].grid(True, alpha=0.3)
        
        # Plot 3: CDF (Cumulative Distribution Function)
        sorted_lats = np.sort(all_lats)
        cdf = np.arange(1, len(sorted_lats) + 1) / len(sorted_lats)
        axes[1, 0].plot(sorted_lats, cdf, linewidth=2)
        axes[1, 0].axhline(0.95, color='r', linestyle='--', alpha=0.7, label='95th Percentile')
        axes[1, 0].axvline(overall_stats['p95'], color='r', linestyle='--', alpha=0.7)
        axes[1, 0].set_xlabel('Latency (seconds)', fontsize=12)
        axes[1, 0].set_ylabel('Cumulative Probability', fontsize=12)
        axes[1, 0].set_title('Cumulative Distribution Function', fontsize=14, fontweight='bold')
        axes[1, 0].legend()
        axes[1, 0].grid(True, alpha=0.3)
        
        # Plot 4: Violin plot
        if model_data:
            parts = axes[1, 1].violinplot(model_data, positions=range(len(model_labels)), 
                                         showmeans=True, showmedians=True)
            axes[1, 1].set_xticks(range(len(model_labels)))
            axes[1, 1].set_xticklabels(model_labels)
            axes[1, 1].set_ylabel('Latency (seconds)', fontsize=12)
            axes[1, 1].set_title('Latency Distribution by Model (Violin Plot)', fontsize=14, fontweight='bold')
            axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, "figures", "latency_distribution.png"), dpi=300, bbox_inches='tight')
        plt.savefig(os.path.join(self.output_dir, "figures", "latency_distribution.pdf"), bbox_inches='tight')
        plt.close()
        
        print(f"✅ Latency distribution plots saved")
    
    def _generate_latency_table(self, overall_stats: Dict, model_stats: Dict):
        """Generate LaTeX table for latency statistics"""
        latex = r"""\begin{table}[htbp]
\centering
\caption{Response Latency Distribution Statistics}
\label{tab:latency_distribution}
\begin{tabular}{lrrrrrr}
\toprule
Model & n & Mean (s) & Median (s) & P95 (s) & P99 (s) & Std (s) \\
\midrule
"""
        
        # Overall row
        latex += f"Overall & {overall_stats['count']} & {overall_stats['mean']:.3f} & {overall_stats['median']:.3f} & {overall_stats['p95']:.3f} & {overall_stats['p99']:.3f} & {overall_stats['std']:.3f} \\\\\n"
        latex += r"\midrule" + "\n"
        
        # Per-model rows
        for model_type in ['gemini', 'local', 'simple']:
            if model_type in model_stats and model_stats[model_type]['count'] > 0:
                stats = model_stats[model_type]
                latex += f"{model_type.capitalize()} & {stats['count']} & {stats['mean']:.3f} & {stats['median']:.3f} & {stats['p95']:.3f} & {stats['p99']:.3f} & {stats['std']:.3f} \\\\\n"
        
        latex += r"""\bottomrule
\end{tabular}
\begin{tablenotes}
\small
\item Note: Latency measured for sequential query processing (batch size = 1).
\item P95 and P99 represent 95th and 99th percentiles respectively.
\end{tablenotes}
\end{table}
"""
        
        with open(os.path.join(self.output_dir, "tables", "latency_table.tex"), 'w', encoding='utf-8') as f:
            f.write(latex)
        
        print("✅ LaTeX latency table generated")
    
    # ==================== REVIEWER COMMENT 2 & 3: Failure Cases ====================
    
    def analyze_language_detection_failures(self, test_cases: List[Dict]):
        """
        Analyze failure cases for language identification
        
        Args:
            test_cases: List of {'text': str, 'true_language': str, 'expected_failure': bool}
        """
        print(f"\n{'='*80}")
        print("🔍 LANGUAGE DETECTION FAILURE ANALYSIS")
        print(f"{'='*80}\n")
        
        failures = []
        
        for i, case in enumerate(test_cases, 1):
            detected_lang = self.chatbot.detect_language(case['text'])
            is_correct = (detected_lang == case['true_language'])
            
            if not is_correct:
                failures.append({
                    'text': case['text'],
                    'true_language': case['true_language'],
                    'detected_language': detected_lang,
                    'text_length': len(case['text']),
                    'has_bengali_chars': bool(re.search(r'[\u0980-\u09FF]', case['text'])),
                    'has_english_chars': bool(re.search(r'[a-zA-Z]', case['text'])),
                    'failure_type': self._categorize_lang_failure(case['text'], detected_lang, case['true_language'])
                })
            
            # Store for confusion matrix
            self.results['language_predictions'].append(detected_lang)
            self.results['language_ground_truth'].append(case['true_language'])
        
        # Analysis
        print(f"Total test cases: {len(test_cases)}")
        print(f"Failures: {len(failures)} ({len(failures)/len(test_cases)*100:.1f}%)")
        
        if failures:
            # Group by failure type
            failure_types = Counter(f['failure_type'] for f in failures)
            print(f"\n📊 Failure Types:")
            for ftype, count in failure_types.most_common():
                print(f"  {ftype}: {count} ({count/len(failures)*100:.1f}%)")
            
            # Save detailed failure cases
            df_failures = pd.DataFrame(failures)
            df_failures.to_csv(os.path.join(self.output_dir, "tables", "language_detection_failures.csv"), index=False)
            
            # Generate failure examples table
            self._generate_language_failure_table(failures[:10])  # Top 10 examples
        
        return failures
    
    def _categorize_lang_failure(self, text: str, detected: str, true: str) -> str:
        """Categorize type of language detection failure"""
        has_bengali = bool(re.search(r'[\u0980-\u09FF]', text))
        has_english = bool(re.search(r'[a-zA-Z]', text))
        
        if has_bengali and has_english:
            return "Code-Switched/Mixed"
        elif len(text) < 20:
            return "Short Text (<20 chars)"
        elif not has_bengali and not has_english:
            return "No Clear Script"
        elif has_bengali and detected == 'en':
            return "Bengali Misclassified as English"
        elif has_english and detected == 'bn':
            return "English Misclassified as Bengali"
        else:
            return "Other"
    
    def analyze_retrieval_failures(self, test_queries: List[Dict]):
        """
        Analyze retrieval misses and failure cases
        
        Args:
            test_queries: List of {'query': str, 'expected_articles': List[str], 'min_relevance_score': float}
        """
        print(f"\n{'='*80}")
        print("🔍 RETRIEVAL FAILURE ANALYSIS")
        print(f"{'='*80}\n")
        
        failures = []
        
        for i, query_config in enumerate(test_queries, 1):
            print(f"Analyzing query {i}/{len(test_queries)}: {query_config['query'][:50]}...")
            
            # Get retrieval results
            result = self.chatbot.process_query(query=query_config['query'], use_llm=False)
            
            # Extract article numbers from sources
            retrieved_articles = set()
            for source in result.get('sources', []):
                if 'article_number' in source:
                    retrieved_articles.add(str(source['article_number']))
            
            expected_articles = set(str(a) for a in query_config.get('expected_articles', []))
            
            # Check for misses
            missed_articles = expected_articles - retrieved_articles
            irrelevant_articles = retrieved_articles - expected_articles
            
            if missed_articles or len(retrieved_articles) == 0:
                failures.append({
                    'query': query_config['query'],
                    'expected_articles': list(expected_articles),
                    'retrieved_articles': list(retrieved_articles),
                    'missed_articles': list(missed_articles),
                    'irrelevant_articles': list(irrelevant_articles),
                    'num_sources': result.get('num_sources', 0),
                    'failure_type': self._categorize_retrieval_failure(
                        len(retrieved_articles),
                        len(missed_articles),
                        len(irrelevant_articles)
                    )
                })
        
        print(f"\nTotal queries: {len(test_queries)}")
        print(f"Retrieval failures: {len(failures)} ({len(failures)/len(test_queries)*100:.1f}%)")
        
        if failures:
            # Group by failure type
            failure_types = Counter(f['failure_type'] for f in failures)
            print(f"\n📊 Retrieval Failure Types:")
            for ftype, count in failure_types.most_common():
                print(f"  {ftype}: {count} ({count/len(failures)*100:.1f}%)")
            
            # Save detailed failures
            df_failures = pd.DataFrame(failures)
            df_failures.to_csv(os.path.join(self.output_dir, "tables", "retrieval_failures.csv"), index=False)
            
            # Generate examples table
            self._generate_retrieval_failure_table(failures[:10])
        
        return failures
    
    def _categorize_retrieval_failure(self, num_retrieved: int, num_missed: int, num_irrelevant: int) -> str:
        """Categorize type of retrieval failure"""
        if num_retrieved == 0:
            return "Complete Miss (0 retrieved)"
        elif num_missed > 0 and num_irrelevant > 0:
            return "Partial Miss with Irrelevant"
        elif num_missed > 0:
            return "Partial Miss"
        elif num_irrelevant > num_retrieved / 2:
            return "Low Precision (>50% irrelevant)"
        else:
            return "Minor Issues"
    
    def _generate_language_failure_table(self, failures: List[Dict]):
        """Generate LaTeX table for language detection failures"""
        latex = r"""\begin{table}[htbp]
\centering
\caption{Language Detection Failure Cases (Examples)}
\label{tab:language_failures}
\begin{tabular}{p{0.4\textwidth}lll}
\toprule
Text Sample & True & Detected & Failure Type \\
\midrule
"""
        
        for failure in failures[:10]:  # Top 10
            text_sample = failure['text'][:50].replace('_', '\\_').replace('&', '\\&')
            if len(failure['text']) > 50:
                text_sample += "..."
            
            latex += f"{text_sample} & {failure['true_language']} & {failure['detected_language']} & {failure['failure_type']} \\\\\n"
        
        latex += r"""\bottomrule
\end{tabular}
\end{table}
"""
        
        with open(os.path.join(self.output_dir, "tables", "language_failure_examples.tex"), 'w', encoding='utf-8') as f:
            f.write(latex)
        
        print("✅ Language failure examples table generated")
    
    def _generate_retrieval_failure_table(self, failures: List[Dict]):
        """Generate LaTeX table for retrieval failures"""
        latex = r"""\begin{table}[htbp]
\centering
\caption{Retrieval Failure Cases (Examples)}
\label{tab:retrieval_failures}
\begin{tabular}{p{0.35\textwidth}p{0.15\textwidth}p{0.15\textwidth}p{0.2\textwidth}}
\toprule
Query & Expected & Retrieved & Failure Type \\
\midrule
"""
        
        for failure in failures[:10]:
            query_sample = failure['query'][:40].replace('_', '\\_').replace('&', '\\&')
            if len(failure['query']) > 40:
                query_sample += "..."
            
            expected = ', '.join(failure['expected_articles'][:3])
            retrieved = ', '.join(failure['retrieved_articles'][:3]) if failure['retrieved_articles'] else 'None'
            
            latex += f"{query_sample} & {expected} & {retrieved} & {failure['failure_type']} \\\\\n"
        
        latex += r"""\bottomrule
\end{tabular}
\end{table}
"""
        
        with open(os.path.join(self.output_dir, "tables", "retrieval_failure_examples.tex"), 'w', encoding='utf-8') as f:
            f.write(latex)
        
        print("✅ Retrieval failure examples table generated")
    
    # ==================== REVIEWER COMMENT 4 & 5: Confusion Matrices ====================
    
    def generate_language_confusion_matrix(self):
        """Generate 3x3 confusion matrix for language identification (English, Bengali, Mixed)"""
        print(f"\n{'='*80}")
        print("📊 LANGUAGE IDENTIFICATION CONFUSION MATRIX")
        print(f"{'='*80}\n")
        
        # Calculate confusion matrix
        labels = ['en', 'bn', 'mixed']
        cm = confusion_matrix(
            self.results['language_ground_truth'],
            self.results['language_predictions'],
            labels=labels
        )
        
        # Calculate percentages (row-normalized)
        cm_percent = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis] * 100
        
        # Calculate metrics
        report = classification_report(
            self.results['language_ground_truth'],
            self.results['language_predictions'],
            labels=labels,
            target_names=['English', 'Bengali', 'Mixed'],
            output_dict=True,
            zero_division=0
        )
        
        # Print metrics
        print("📈 Per-Class Metrics:")
        for lang, metrics in report.items():
            if isinstance(metrics, dict):
                print(f"\n  {lang}:")
                print(f"    Precision: {metrics['precision']:.3f}")
                print(f"    Recall:    {metrics['recall']:.3f}")
                print(f"    F1-Score:  {metrics['f1-score']:.3f}")
                print(f"    Support:   {metrics['support']}")
        
        print(f"\n📊 Macro Average:")
        print(f"  Precision: {report['macro avg']['precision']:.3f}")
        print(f"  Recall:    {report['macro avg']['recall']:.3f}")
        print(f"  F1-Score:  {report['macro avg']['f1-score']:.3f}")
        
        print(f"\n📊 Weighted Average:")
        print(f"  Precision: {report['weighted avg']['precision']:.3f}")
        print(f"  Recall:    {report['weighted avg']['recall']:.3f}")
        print(f"  F1-Score:  {report['weighted avg']['f1-score']:.3f}")
        
        # Visualize confusion matrix
        self._plot_confusion_matrix(
            cm, cm_percent, labels,
            title="Language Identification Confusion Matrix",
            filename="language_confusion_matrix"
        )
        
        # Generate LaTeX table
        self._generate_confusion_matrix_table(
            cm, cm_percent, labels,
            caption="Language Identification Confusion Matrix",
            label="tab:lang_confusion",
            filename="language_confusion_matrix.tex"
        )
        
        return cm, report
    
    def generate_scope_confusion_matrix(self, threshold: float = 0.5):
        """
        Generate 2x2 confusion matrix for scope validator (In-scope vs Out-of-scope)
        
        Args:
            threshold: Decision threshold for scope classification
        """
        print(f"\n{'='*80}")
        print(f"📊 SCOPE VALIDATOR CONFUSION MATRIX (threshold={threshold})")
        print(f"{'='*80}\n")
        
        labels = ['in_scope', 'out_of_scope']
        cm = confusion_matrix(
            self.results['scope_ground_truth'],
            self.results['scope_predictions'],
            labels=labels
        )
        
        # Calculate percentages
        cm_percent = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis] * 100
        
        # Calculate metrics
        report = classification_report(
            self.results['scope_ground_truth'],
            self.results['scope_predictions'],
            labels=labels,
            target_names=['In-Scope (Constitutional)', 'Out-of-Scope'],
            output_dict=True,
            zero_division=0
        )
        
        # Calculate class priors
        total = len(self.results['scope_ground_truth'])
        priors = {
            'in_scope': sum(1 for x in self.results['scope_ground_truth'] if x == 'in_scope') / total,
            'out_of_scope': sum(1 for x in self.results['scope_ground_truth'] if x == 'out_of_scope') / total
        }
        
        # Print results
        print(f"📈 Class Priors:")
        print(f"  In-Scope:     {priors['in_scope']:.3f} ({priors['in_scope']*100:.1f}%)")
        print(f"  Out-of-Scope: {priors['out_of_scope']:.3f} ({priors['out_of_scope']*100:.1f}%)")
        
        print(f"\n📈 Per-Class Metrics:")
        for scope, metrics in report.items():
            if isinstance(metrics, dict):
                print(f"\n  {scope}:")
                print(f"    Precision: {metrics['precision']:.3f}")
                print(f"    Recall:    {metrics['recall']:.3f}")
                print(f"    F1-Score:  {metrics['f1-score']:.3f}")
                print(f"    Support:   {metrics['support']}")
        
        print(f"\n📊 Macro Average:")
        print(f"  F1-Score: {report['macro avg']['f1-score']:.3f}")
        
        print(f"\n📊 Micro Average:")
        print(f"  F1-Score: {report['accuracy']:.3f}")  # Micro F1 = Accuracy for binary
        
        print(f"\n📊 Weighted Average:")
        print(f"  F1-Score: {report['weighted avg']['f1-score']:.3f}")
        
        # Visualize
        self._plot_confusion_matrix(
            cm, cm_percent, ['In-Scope', 'Out-of-Scope'],
            title=f"Scope Validator Confusion Matrix (threshold={threshold})",
            filename="scope_confusion_matrix"
        )
        
        # Generate LaTeX table
        self._generate_scope_confusion_latex(cm, cm_percent, priors, report, threshold)
        
        return cm, report, priors
    
    def _plot_confusion_matrix(self, cm: np.ndarray, cm_percent: np.ndarray, 
                               labels: List[str], title: str, filename: str):
        """Plot confusion matrix with both counts and percentages"""
        fig, axes = plt.subplots(1, 2, figsize=(16, 6))
        
        # Plot 1: Raw counts
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                   xticklabels=labels, yticklabels=labels,
                   cbar_kws={'label': 'Count'}, ax=axes[0])
        axes[0].set_xlabel('Predicted Label', fontsize=12)
        axes[0].set_ylabel('True Label', fontsize=12)
        axes[0].set_title(f'{title}\n(Raw Counts)', fontsize=14, fontweight='bold')
        
        # Plot 2: Percentages
        sns.heatmap(cm_percent, annot=True, fmt='.1f', cmap='Blues',
                   xticklabels=labels, yticklabels=labels,
                   cbar_kws={'label': 'Percentage (%)'}, ax=axes[1])
        axes[1].set_xlabel('Predicted Label', fontsize=12)
        axes[1].set_ylabel('True Label', fontsize=12)
        axes[1].set_title(f'{title}\n(Row-Normalized %)', fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, "figures", f"{filename}.png"), dpi=300, bbox_inches='tight')
        plt.savefig(os.path.join(self.output_dir, "figures", f"{filename}.pdf"), bbox_inches='tight')
        plt.close()
        
        print(f"✅ Confusion matrix plots saved: {filename}")
    
    def _generate_confusion_matrix_table(self, cm: np.ndarray, cm_percent: np.ndarray,
                                        labels: List[str], caption: str, label: str, filename: str):
        """Generate LaTeX table for confusion matrix"""
        latex = f"""\\begin{{table}}[htbp]
\\centering
\\caption{{{caption}}}
\\label{{{label}}}
\\begin{{tabular}}{{l{'c' * len(labels)}}}
\\toprule
& \\multicolumn{{{len(labels)}}}{{c}}{{Predicted}} \\\\
\\cmidrule{{2-{len(labels)+1}}}
True & {' & '.join(labels)} \\\\
\\midrule
"""
        
        for i, true_label in enumerate(labels):
            row = [true_label]
            for j in range(len(labels)):
                row.append(f"{cm[i,j]} ({cm_percent[i,j]:.1f}\\%)")
            latex += ' & '.join(row) + " \\\\\n"
        
        latex += r"""\bottomrule
\end{tabular}
\begin{tablenotes}
\small
\item Note: Values shown as Count (Row-Normalized \%).
\end{tablenotes}
\end{table}
"""
        
        with open(os.path.join(self.output_dir, "tables", filename), 'w', encoding='utf-8') as f:
            f.write(latex)
        
        print(f"✅ Confusion matrix table saved: {filename}")
    
    def _generate_scope_confusion_latex(self, cm: np.ndarray, cm_percent: np.ndarray,
                                       priors: Dict, report: Dict, threshold: float):
        """Generate comprehensive LaTeX table for scope confusion matrix"""
        latex = f"""\\begin{{table}}[htbp]
\\centering
\\caption{{Scope Validator Confusion Matrix and Metrics (threshold={threshold})}}
\\label{{tab:scope_confusion}}
\\begin{{tabular}}{{lcccc}}
\\toprule
& \\multicolumn{{2}}{{c}}{{Predicted}} & & \\\\
\\cmidrule{{2-3}}
True & In-Scope & Out-of-Scope & Precision & Recall \\\\
\\midrule
In-Scope & {cm[0,0]} ({cm_percent[0,0]:.1f}\\%) & {cm[0,1]} ({cm_percent[0,1]:.1f}\\%) & {report['In-Scope (Constitutional)']['precision']:.3f} & {report['In-Scope (Constitutional)']['recall']:.3f} \\\\
Out-of-Scope & {cm[1,0]} ({cm_percent[1,0]:.1f}\\%) & {cm[1,1]} ({cm_percent[1,1]:.1f}\\%) & {report['Out-of-Scope']['precision']:.3f} & {report['Out-of-Scope']['recall']:.3f} \\\\
\\midrule
\\multicolumn{{5}}{{l}}{{\\textbf{{Aggregate Metrics}}}} \\\\
\\midrule
Macro F1 & \\multicolumn{{4}}{{c}}{{{report['macro avg']['f1-score']:.3f}}} \\\\
Micro F1 & \\multicolumn{{4}}{{c}}{{{report['accuracy']:.3f}}} \\\\
Weighted F1 & \\multicolumn{{4}}{{c}}{{{report['weighted avg']['f1-score']:.3f}}} \\\\
\\midrule
\\multicolumn{{5}}{{l}}{{\\textbf{{Class Priors}}}} \\\\
\\midrule
In-Scope & \\multicolumn{{4}}{{c}}{{{priors['in_scope']:.3f} ({priors['in_scope']*100:.1f}\\%)}} \\\\
Out-of-Scope & \\multicolumn{{4}}{{c}}{{{priors['out_of_scope']:.3f} ({priors['out_of_scope']*100:.1f}\\%)}} \\\\
\\bottomrule
\\end{{tabular}}
\\begin{{tablenotes}}
\\small
\\item Note: Confusion matrix values shown as Count (Row-Normalized \\%).
\\item Decision threshold for scope classification: {threshold}
\\end{{tablenotes}}
\\end{{table}}
"""
        
        with open(os.path.join(self.output_dir, "tables", "scope_confusion_detailed.tex"), 'w', encoding='utf-8') as f:
            f.write(latex)
        
        print("✅ Detailed scope confusion matrix table generated")
    
    # ==================== REVIEWER COMMENT 5: Precision-Recall Curves ====================
    
    def generate_precision_recall_curves(self, retrieval_results: List[Dict]):
        """
        Generate precision-recall curves for retrieval system
        
        Args:
            retrieval_results: List of {'query': str, 'scores': List[float], 'relevance': List[int]}
        """
        print(f"\n{'='*80}")
        print("📊 PRECISION-RECALL CURVES FOR RETRIEVAL")
        print(f"{'='*80}\n")
        
        all_scores = []
        all_relevance = []
        
        for result in retrieval_results:
            all_scores.extend(result['scores'])
            all_relevance.extend(result['relevance'])
            
            self.results['retrieval_scores'].extend(result['scores'])
            self.results['retrieval_relevance'].extend(result['relevance'])
        
        # Calculate precision-recall curve
        precision, recall, thresholds = precision_recall_curve(all_relevance, all_scores)
        ap_score = average_precision_score(all_relevance, all_scores)
        
        print(f"Average Precision Score: {ap_score:.3f}")
        
        # Plot PR curve
        fig, axes = plt.subplots(1, 2, figsize=(15, 6))
        
        # Plot 1: Precision-Recall Curve
        axes[0].plot(recall, precision, linewidth=2, label=f'AP = {ap_score:.3f}')
        axes[0].fill_between(recall, precision, alpha=0.3)
        axes[0].set_xlabel('Recall', fontsize=12)
        axes[0].set_ylabel('Precision', fontsize=12)
        axes[0].set_title('Precision-Recall Curve', fontsize=14, fontweight='bold')
        axes[0].legend(loc='best', fontsize=11)
        axes[0].grid(True, alpha=0.3)
        axes[0].set_xlim([0.0, 1.0])
        axes[0].set_ylim([0.0, 1.05])
        
        # Plot 2: Precision vs Threshold
        axes[1].plot(thresholds, precision[:-1], 'b-', linewidth=2, label='Precision')
        axes[1].plot(thresholds, recall[:-1], 'g-', linewidth=2, label='Recall')
        axes[1].set_xlabel('Decision Threshold', fontsize=12)
        axes[1].set_ylabel('Score', fontsize=12)
        axes[1].set_title('Precision/Recall vs Threshold', fontsize=14, fontweight='bold')
        axes[1].legend(loc='best', fontsize=11)
        axes[1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, "figures", "precision_recall_curve.png"), dpi=300, bbox_inches='tight')
        plt.savefig(os.path.join(self.output_dir, "figures", "precision_recall_curve.pdf"), bbox_inches='tight')
        plt.close()
        
        print("✅ Precision-recall curves saved")
        
        return precision, recall, ap_score
    
    def calculate_recall_at_k(self, retrieval_results: List[Dict], k_values: List[int] = [1, 3, 5, 10]):
        """
        Calculate Recall@k for different k values
        
        Args:
            retrieval_results: List of {'query': str, 'ranked_results': List[Dict], 'relevant_docs': Set}
            k_values: List of k values to evaluate
        """
        print(f"\n{'='*80}")
        print("📊 RECALL@K METRICS")
        print(f"{'='*80}\n")
        
        recall_at_k = {k: [] for k in k_values}
        
        for result in retrieval_results:
            relevant_docs = set(result['relevant_docs'])
            ranked_results = result['ranked_results']
            
            for k in k_values:
                retrieved_at_k = set(r['doc_id'] for r in ranked_results[:k])
                if len(relevant_docs) > 0:
                    recall_k = len(retrieved_at_k & relevant_docs) / len(relevant_docs)
                else:
                    recall_k = 0.0
                recall_at_k[k].append(recall_k)
        
        # Calculate mean Recall@k
        mean_recall_at_k = {k: np.mean(scores) for k, scores in recall_at_k.items()}
        
        print("📈 Mean Recall@k:")
        for k, score in mean_recall_at_k.items():
            print(f"  Recall@{k}: {score:.3f}")
        
        # Plot Recall@k
        fig, ax = plt.subplots(figsize=(10, 6))
        
        k_list = sorted(mean_recall_at_k.keys())
        recall_list = [mean_recall_at_k[k] for k in k_list]
        
        ax.plot(k_list, recall_list, 'o-', linewidth=2, markersize=8)
        ax.set_xlabel('k (Number of Retrieved Documents)', fontsize=12)
        ax.set_ylabel('Mean Recall@k', fontsize=12)
        ax.set_title('Recall@k Performance', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.set_ylim([0.0, 1.05])
        
        # Add value labels
        for k, recall in zip(k_list, recall_list):
            ax.annotate(f'{recall:.3f}', xy=(k, recall), 
                       xytext=(0, 10), textcoords='offset points',
                       ha='center', fontsize=10)
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, "figures", "recall_at_k.png"), dpi=300, bbox_inches='tight')
        plt.savefig(os.path.join(self.output_dir, "figures", "recall_at_k.pdf"), bbox_inches='tight')
        plt.close()
        
        # Generate LaTeX table
        self._generate_recall_at_k_table(mean_recall_at_k)
        
        print("✅ Recall@k analysis complete")
        
        return mean_recall_at_k
    
    def _generate_recall_at_k_table(self, recall_at_k: Dict[int, float]):
        """Generate LaTeX table for Recall@k"""
        latex = r"""\begin{table}[htbp]
\centering
\caption{Recall@k Performance Metrics}
\label{tab:recall_at_k}
\begin{tabular}{cc}
\toprule
k & Mean Recall@k \\
\midrule
"""
        
        for k in sorted(recall_at_k.keys()):
            latex += f"{k} & {recall_at_k[k]:.3f} \\\\\n"
        
        latex += r"""\bottomrule
\end{tabular}
\begin{tablenotes}
\small
\item Note: Recall@k measures the proportion of relevant documents retrieved in top-k results.
\end{tablenotes}
\end{table}
"""
        
        with open(os.path.join(self.output_dir, "tables", "recall_at_k.tex"), 'w', encoding='utf-8') as f:
            f.write(latex)
        
        print("✅ Recall@k table generated")
    
    # ==================== Query Set for Reproducibility ====================
    
    def _convert_sets_to_lists(self, obj):
        """Recursively convert sets to lists for JSON serialization"""
        if isinstance(obj, set):
            return list(obj)
        elif isinstance(obj, dict):
            return {key: self._convert_sets_to_lists(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_sets_to_lists(item) for item in obj]
        else:
            return obj
    
    def export_query_set(self, queries: List[Dict], filename: str = "evaluation_query_set.json"):
        """
        Export query set for reproducibility
        
        Args:
            queries: List of query configurations
            filename: Output filename
        """
        print(f"\n{'='*80}")
        print("📝 EXPORTING QUERY SET FOR REPRODUCIBILITY")
        print(f"{'='*80}\n")
        
        # Convert sets to lists for JSON serialization
        queries_serializable = self._convert_sets_to_lists(queries)
        
        query_set = {
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'total_queries': len(queries) if isinstance(queries, list) else sum(len(v) if isinstance(v, list) else 1 for v in queries.values()),
                'version': '1.0',
                'system': 'Bangladesh Constitution Chatbot'
            },
            'queries': queries_serializable
        }
        
        output_path = os.path.join(self.output_dir, "data", filename)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(query_set, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Query set exported: {output_path}")
        print(f"   Total queries: {len(queries)}")
        
        return output_path
    
    def generate_summary_report(self):
        """Generate comprehensive summary report"""
        print(f"\n{'='*80}")
        print("📄 GENERATING SUMMARY REPORT")
        print(f"{'='*80}\n")
        
        report = f"""
# Evaluation Summary Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Overview
- Total evaluations performed: {len(self.results['latency'])}
- Output directory: {self.output_dir}

## Files Generated

### Figures
- latency_distribution.png/pdf
- language_confusion_matrix.png/pdf
- scope_confusion_matrix.png/pdf
- precision_recall_curve.png/pdf
- recall_at_k.png/pdf

### Tables (LaTeX)
- latency_table.tex
- language_confusion_matrix.tex
- scope_confusion_detailed.tex
- recall_at_k.tex
- language_failure_examples.tex
- retrieval_failure_examples.tex

### Data
- latency_distribution.csv
- language_detection_failures.csv
- retrieval_failures.csv
- evaluation_query_set.json

## Key Findings

All metrics have been calculated according to reviewer requirements:
1. ✅ Latency distribution with mean, median, P95
2. ✅ Failure cases for language identification
3. ✅ Failure cases for retrieval misses
4. ✅ Language ID 3x3 confusion matrix
5. ✅ Scope validator 2x2 confusion matrix with class priors
6. ✅ Precision-recall curves for retrieval
7. ✅ Recall@k metrics
8. ✅ Query set for reproducibility

## Next Steps
1. Review all generated figures and tables
2. Incorporate into paper manuscript
3. Update methodology section with detailed metrics
4. Add failure analysis discussion
"""
        
        with open(os.path.join(self.output_dir, "SUMMARY_REPORT.md"), 'w', encoding='utf-8') as f:
            f.write(report)
        
        print("✅ Summary report generated")
        print(f"\n📁 All results saved to: {self.output_dir}/")
        
        return report


def main():
    """Main execution function"""
    print("="*80)
    print("BANGLADESH CONSTITUTION CHATBOT - PAPER EVALUATION SYSTEM")
    print("="*80)
    
    evaluator = PaperEvaluationSystem()
    
    # Initialize chatbot
    evaluator.initialize_chatbot()
    
    # TODO: Add your test data here
    # This is a template - you'll need to populate with actual test cases
    
    print("\n⚠️  This is a template evaluation system.")
    print("Please populate with your actual test data in run_paper_evaluation.py")
    
    return evaluator


if __name__ == "__main__":
    evaluator = main()
