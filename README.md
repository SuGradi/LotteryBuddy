# LotteryBuddy

一个自动推荐彩票号码并检查开奖结果的工具。

## 功能特点

- 自动推荐大乐透和双色球号码
- 自动检查开奖结果
- 通过邮件发送推荐号码和开奖结果
- 使用 GitHub Actions 自动运行
- 数据存储在 GitHub 仓库中

## 设置步骤

1. Fork 本仓库到您的 GitHub 账号

2. 在仓库设置中添加以下 Secrets：
   - `EMAIL_USER`: 发件人邮箱地址
   - `EMAIL_PASSWORD`: 邮箱授权码（QQ邮箱使用授权码）
   - `RECIPIENT_EMAIL`: 收件人邮箱地址
   - `GITHUB_TOKEN`: GitHub Personal Access Token（需要有 repo 权限）

3. 修改 GitHub Actions 工作流文件中的仓库信息：
   - 在 `.github/workflows/lottery.yml` 中设置正确的仓库名称

4. 启用 GitHub Actions：
   - 在仓库的 Actions 标签页中启用工作流
   - 工作流会在每天早上9点和晚上21点自动运行

## 运行时间

- 推荐号码：每天早上9点（北京时间）
- 开奖检查：每天晚上21点（北京时间）

## 数据存储

- 推荐号码按月份存储在 `data` 目录下
- 文件名格式：`recommended_numbers_YYYY-MM.json`
- 可以通过 GitHub 仓库查看历史记录

## 手动触发

如果需要手动运行程序，可以：

1. 在 GitHub 仓库的 Actions 标签页中
2. 选择 "Lottery Recommendation and Check" 工作流
3. 点击 "Run workflow" 按钮

## 注意事项

- 确保邮箱设置正确，特别是授权码
- GitHub Token 需要有足够的权限
- 建议使用 QQ 邮箱，其他邮箱可能需要调整 SMTP 设置
