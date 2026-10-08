import os
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier

# Set aesthetic styling
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['font.size'] = 10
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['axes.labelsize'] = 11

# File paths
full_csv = 'diabetes_binary_health_indicators_BRFSS2015.csv'
split_csv = 'diabetes_binary_5050split_health_indicators_BRFSS2015.csv'
multiclass_csv = 'diabetes_012_health_indicators_BRFSS2015.csv'
fig_dir = 'review1/figures'
os.makedirs(fig_dir, exist_ok=True)

print("Loading datasets...")
df_full = pd.read_csv(full_csv)
df_split = pd.read_csv(split_csv)
df_multi = pd.read_csv(multiclass_csv)

# 1. Compute summary stats
stats_dict = {}

# Target counts
stats_dict['full_shape'] = list(df_full.shape)
stats_dict['split_shape'] = list(df_split.shape)
stats_dict['full_target'] = df_full['Diabetes_binary'].value_counts().to_dict()
stats_dict['multi_target'] = df_multi['Diabetes_012'].value_counts().to_dict()

# Descriptive statistics for numerical/ordinal columns
desc = df_full.describe().T[['mean', 'std', 'min', '50%', 'max']]
desc.columns = ['Mean', 'Std', 'Min', 'Median', 'Max']
stats_dict['descriptive_stats'] = desc.to_dict(orient='index')

# Correlations with target
corr_full = df_full.corr()['Diabetes_binary'].sort_values(ascending=False)
stats_dict['correlations'] = corr_full.to_dict()

# Save json metrics
with open('review1/eda_metrics.json', 'w') as f:
    json.dump(stats_dict, f, indent=2)

print("Saved eda_metrics.json")

# --- GENERATE FIGURES ---

# Figure 1: Target Distribution (Full vs 50/50 Split)
fig, axes = plt.subplots(1, 2, figsize=(12, 5))
sns.countplot(x='Diabetes_binary', data=df_full, ax=axes[0], palette=['#4C72B0', '#C44E52'])
axes[0].set_title('Full Dataset (N=253,680)\n86.1% No Diabetes | 13.9% Diabetes')
axes[0].set_xticklabels(['No Diabetes (0)', 'Prediabetes/Diabetes (1)'])
axes[0].set_ylabel('Respondent Count')

for p in axes[0].patches:
    axes[0].annotate(f'{int(p.get_height()):,}\n({p.get_height()/len(df_full)*100:.1f}%)',
                     (p.get_x() + p.get_width() / 2., p.get_height() / 2),
                     ha='center', va='center', color='white', fontweight='bold')

sns.countplot(x='Diabetes_binary', data=df_split, ax=axes[1], palette=['#4C72B0', '#C44E52'])
axes[1].set_title('Balanced 50/50 Split Dataset (N=70,692)\n50.0% No Diabetes | 50.0% Diabetes')
axes[1].set_xticklabels(['No Diabetes (0)', 'Prediabetes/Diabetes (1)'])
axes[1].set_ylabel('Respondent Count')

for p in axes[1].patches:
    axes[1].annotate(f'{int(p.get_height()):,}\n({p.get_height()/len(df_split)*100:.1f}%)',
                     (p.get_x() + p.get_width() / 2., p.get_height() / 2),
                     ha='center', va='center', color='white', fontweight='bold')

plt.tight_layout()
plt.savefig(os.path.join(fig_dir, '01_target_distribution.png'), dpi=300)
plt.close()

# Figure 2: Correlation Heatmap
plt.figure(figsize=(14, 10))
corr_matrix = df_full.corr()
mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
sns.heatmap(corr_matrix, mask=mask, annot=True, fmt='.2f', cmap='coolwarm', vmin=-0.4, vmax=0.8,
            linewidths=0.5, cbar_kws={"shrink": .8})
plt.title('BRFSS 2015 Feature Correlation Matrix', fontsize=14, pad=15)
plt.tight_layout()
plt.savefig(os.path.join(fig_dir, '02_correlation_heatmap.png'), dpi=300)
plt.close()

# Figure 3: BMI Distribution by Diabetes Status
plt.figure(figsize=(10, 5))
sns.kdeplot(data=df_full[df_full['Diabetes_binary']==0]['BMI'], label='No Diabetes', color='#4C72B0', shade=True, bw_adjust=1.5)
sns.kdeplot(data=df_full[df_full['Diabetes_binary']==1]['BMI'], label='Diabetes/Prediabetes', color='#C44E52', shade=True, bw_adjust=1.5)
plt.axvline(25, color='orange', linestyle='--', label='Overweight Threshold (BMI=25)')
plt.axvline(30, color='red', linestyle='--', label='Obese Threshold (BMI=30)')
plt.xlim(12, 60)
plt.title('BMI Density Distribution by Diabetes Status')
plt.xlabel('Body Mass Index (BMI)')
plt.ylabel('Density')
plt.legend()
plt.tight_layout()
plt.savefig(os.path.join(fig_dir, '03_bmi_distribution.png'), dpi=300)
plt.close()

# Figure 4: Comorbidity Rates (HighBP, HighChol, HeartDiseaseorAttack, Stroke)
comorbidities = ['HighBP', 'HighChol', 'HeartDiseaseorAttack', 'Stroke', 'DiffWalk']
df_com = df_full.groupby('Diabetes_binary')[comorbidities].mean().reset_index()
df_com_melted = pd.melt(df_com, id_vars=['Diabetes_binary'], var_name='Condition', value_name='Prevalence')
df_com_melted['Diabetes'] = df_com_melted['Diabetes_binary'].map({0: 'No Diabetes', 1: 'Diabetes'})

plt.figure(figsize=(10, 5))
ax = sns.barplot(x='Condition', y='Prevalence', hue='Diabetes', data=df_com_melted, palette=['#4C72B0', '#C44E52'])
plt.title('Clinical Comorbidity Prevalence by Diabetes Status')
plt.ylabel('Prevalence Rate (0.0 to 1.0)')
plt.ylim(0, 1.0)
for p in ax.patches:
    h = p.get_height()
    if h > 0:
        ax.annotate(f'{h*100:.1f}%', (p.get_x() + p.get_width() / 2., h + 0.02),
                    ha='center', va='bottom', fontsize=9)
plt.tight_layout()
plt.savefig(os.path.join(fig_dir, '04_comorbidity_analysis.png'), dpi=300)
plt.close()

# Figure 5: Age Category vs Diabetes Prevalence
age_stats = df_full.groupby('Age')['Diabetes_binary'].agg(['count', 'mean']).reset_index()
age_labels = ['18-24','25-29','30-34','35-39','40-44','45-49','50-54','55-59','60-64','65-69','70-74','75-79','80+']
age_stats['Age_Group'] = age_labels

fig, ax1 = plt.subplots(figsize=(12, 5))
ax2 = ax1.twinx()
sns.barplot(x='Age_Group', y='count', data=age_stats, ax=ax1, color='#AEC7E8', alpha=0.7)
sns.lineplot(x='Age_Group', y='mean', data=age_stats, ax=ax2, color='#C44E52', marker='o', linewidth=2.5, label='Diabetes Prevalence')

ax1.set_xlabel('Age Category (BRFSS 1-13)')
ax1.set_ylabel('Sample Count', color='#1F77B4')
ax2.set_ylabel('Diabetes Prevalence Rate', color='#C44E52')
ax2.set_ylim(0, 0.35)
plt.title('Diabetes Prevalence across Age Categories')
for i, rate in enumerate(age_stats['mean']):
    ax2.annotate(f'{rate*100:.1f}%', (i, rate + 0.015), ha='center', fontsize=8, color='#C44E52', fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(fig_dir, '05_age_distribution.png'), dpi=300)
plt.close()

# Figure 6: Lifestyle Factors vs Diabetes
lifestyle = ['PhysActivity', 'Smoker', 'Fruits', 'Veggies', 'HvyAlcoholConsump']
df_life = df_full.groupby('Diabetes_binary')[lifestyle].mean().reset_index()
df_life_melted = pd.melt(df_life, id_vars=['Diabetes_binary'], var_name='Lifestyle', value_name='Prevalence')
df_life_melted['Diabetes'] = df_life_melted['Diabetes_binary'].map({0: 'No Diabetes', 1: 'Diabetes'})

plt.figure(figsize=(10, 5))
ax = sns.barplot(x='Lifestyle', y='Prevalence', hue='Diabetes', data=df_life_melted, palette=['#4C72B0', '#C44E52'])
plt.title('Lifestyle Behaviors by Diabetes Status')
plt.ylabel('Adherence / Prevalence Rate')
plt.ylim(0, 1.0)
for p in ax.patches:
    h = p.get_height()
    if h > 0:
        ax.annotate(f'{h*100:.1f}%', (p.get_x() + p.get_width() / 2., h + 0.02),
                    ha='center', va='bottom', fontsize=9)
plt.tight_layout()
plt.savefig(os.path.join(fig_dir, '06_lifestyle_factors.png'), dpi=300)
plt.close()

# Figure 7: General Health Rating vs Diabetes
gen_stats = df_full.groupby('GenHlth')['Diabetes_binary'].agg(['count', 'mean']).reset_index()
gen_labels = ['1: Excellent', '2: Very Good', '3: Good', '4: Fair', '5: Poor']
gen_stats['GenHlth_Label'] = gen_labels

plt.figure(figsize=(9, 5))
ax = sns.barplot(x='GenHlth_Label', y='mean', data=gen_stats, palette='Blues_r')
plt.title('Diabetes Prevalence by Self-Reported General Health Rating')
plt.xlabel('General Health Rating (GenHlth)')
plt.ylabel('Diabetes Prevalence Rate')
plt.ylim(0, 0.5)
for p in ax.patches:
    h = p.get_height()
    ax.annotate(f'{h*100:.1f}%', (p.get_x() + p.get_width() / 2., h + 0.015),
                ha='center', va='bottom', fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(fig_dir, '07_genhealth_vs_diabetes.png'), dpi=300)
plt.close()

# Figure 8: Random Forest Feature Importance
X = df_split.drop(columns=['Diabetes_binary'])
y = df_split['Diabetes_binary']

rf = RandomForestClassifier(n_estimators=100, random_state=42)
rf.fit(X, y)

feat_imp = pd.Series(rf.feature_importances_, index=X.columns).sort_values(ascending=True)

plt.figure(figsize=(10, 7))
feat_imp.plot(kind='barh', color='#2CA02C')
plt.title('Random Forest Feature Importance for Diabetes Classification (50/50 Split)')
plt.xlabel('Importance Score (Gini Impurity Reduction)')
plt.tight_layout()
plt.savefig(os.path.join(fig_dir, '08_feature_importance.png'), dpi=300)
plt.close()

print("All 8 figures successfully generated and saved to review1/figures/")
