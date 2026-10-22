using System;
using System.Drawing;
using System.Drawing.Drawing2D;
using System.IO;
using System.Media;
using System.Windows.Forms;
using System.Xml.Linq;

namespace PomodoroApp
{
    enum Phase { Focus, ShortBreak, LongBreak }

    sealed class ClockFace : Control
    {
        public double Progress { get; set; }
        public string TimeText { get; set; }
        public string PhaseText { get; set; }
        public string StatusText { get; set; }
        public bool TimeOnly { get; set; }

        public ClockFace()
        {
            DoubleBuffered = true;
            TimeText = "25:00";
            PhaseText = "专注时间";
            StatusText = "准备开始";
            BackColor = Color.FromArgb(25, 43, 40);
            ForeColor = Color.FromArgb(245, 250, 247);
        }

        protected override void OnPaint(PaintEventArgs e)
        {
            base.OnPaint(e);
            e.Graphics.SmoothingMode = SmoothingMode.AntiAlias;
            e.Graphics.TextRenderingHint = System.Drawing.Text.TextRenderingHint.AntiAlias;
            if (TimeOnly)
            {
                using (Font timeFont = new Font("Segoe UI", 18, FontStyle.Bold))
                using (Brush main = new SolidBrush(ForeColor))
                using (StringFormat centered = new StringFormat { Alignment = StringAlignment.Center, LineAlignment = StringAlignment.Center })
                    e.Graphics.DrawString(TimeText, timeFont, main, ClientRectangle, centered);
                return;
            }
            bool small = Math.Min(Width, Height) < 200;
            int stroke = small ? 5 : 12;
            int diameter = Math.Max(1, Math.Min(Width, Height) - stroke - 12);
            Rectangle ring = new Rectangle((Width - diameter) / 2, (Height - diameter) / 2, diameter, diameter);
            using (Pen track = new Pen(Color.FromArgb(55, 83, 76), stroke))
            using (Pen active = new Pen(Color.FromArgb(239, 128, 107), stroke))
            {
                track.StartCap = track.EndCap = LineCap.Round;
                active.StartCap = active.EndCap = LineCap.Round;
                e.Graphics.DrawArc(track, ring, -90, 360);
                if (Progress > 0) e.Graphics.DrawArc(active, ring, -90, (float)(360 * Math.Min(1, Progress)));
            }
            float scale = Math.Min(1f, Math.Min(Width, Height) / 360f);
            using (Font phaseFont = new Font("Microsoft YaHei", small ? 8 : 12 * scale))
            using (Font timeFont = new Font("Segoe UI", small ? 20 : 53 * scale, FontStyle.Bold))
            using (Font statusFont = new Font("Microsoft YaHei", small ? 8 : 11 * scale))
            using (Brush main = new SolidBrush(ForeColor))
            using (Brush muted = new SolidBrush(Color.FromArgb(188, 206, 198)))
            {
                DrawCentered(e.Graphics, PhaseText, phaseFont, muted, Height / 2 - (small ? 34 : 78 * scale));
                DrawCentered(e.Graphics, TimeText, timeFont, main, Height / 2 - (small ? 16 : 53 * scale));
                DrawCentered(e.Graphics, StatusText, statusFont, muted, Height / 2 + (small ? 21 : 52 * scale));
            }
        }

        private void DrawCentered(Graphics graphics, string value, Font font, Brush brush, float y)
        {
            SizeF size = graphics.MeasureString(value, font);
            graphics.DrawString(value, font, brush, (Width - size.Width) / 2, y);
        }
    }

    sealed class MainForm : Form
    {
        private readonly Color dark = Color.FromArgb(25, 43, 40);
        private readonly Color paper = Color.FromArgb(244, 247, 245);
        private readonly Color coral = Color.FromArgb(239, 128, 107);
        private readonly string statePath;
        private readonly int[] minutes = { 25, 5, 15 };
        private readonly Button[] modeButtons = new Button[3];
        private readonly NumericUpDown[] durationInputs = new NumericUpDown[3];
        private readonly ClockFace face = new ClockFace();
        private readonly Label countLabel = new Label();
        private readonly Label untilLabel = new Label();
        private readonly Label nextLabel = new Label();
        private readonly Button startButton = new Button();
        private readonly CheckBox soundBox = new CheckBox();
        private readonly Timer timer = new Timer();
        private Phase phase = Phase.Focus;
        private int completed;
        private int remaining;
        private DateTime? deadline;
        private DateTime statisticsDay = DateTime.Today;
        private string notice;
        private bool soundEnabled = true;
        private bool timeOnly;
        private Size expandedSize = new Size(920, 680);
        private Point dragOrigin;

        public MainForm()
        {
            Text = "番茄时钟";
            StartPosition = FormStartPosition.CenterScreen;
            MinimumSize = new Size(200, 200);
            Size = new Size(920, 680);
            BackColor = paper;
            Font = new Font("Microsoft YaHei", 10);
            AutoScaleMode = AutoScaleMode.Dpi;
            statePath = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "PomodoroClock", "state.xml");
            LoadState();
            BuildUi();
            RefreshUi();
            timer.Interval = 250;
            timer.Tick += (sender, args) => TickClock();
            timer.Start();
            FormClosing += (sender, args) => SaveState();
        }

        private void BuildUi()
        {
            Panel left = new Panel { Dock = DockStyle.Fill, BackColor = dark };
            Panel right = new Panel { Dock = DockStyle.Right, Width = 310, BackColor = paper };
            Controls.Add(left);
            Controls.Add(right);

            Label brand = TextLabel("●  番茄时钟", 15, Color.White, true);
            brand.SetBounds(34, 27, 250, 35);
            left.Controls.Add(brand);

            soundBox.Text = "完成提示音";
            soundBox.Checked = soundEnabled;
            soundBox.ForeColor = Color.FromArgb(193, 210, 205);
            soundBox.BackColor = dark;
            soundBox.AutoSize = true;
            soundBox.Anchor = AnchorStyles.Top | AnchorStyles.Right;
            soundBox.Location = new Point(left.Width - 145, 37);
            soundBox.CheckedChanged += (sender, args) => SaveState();
            left.Controls.Add(soundBox);

            Button compactButton = new Button { Text = "缩小", Left = 205, Top = 42, Width = 72, Height = 30, BackColor = paper, ForeColor = dark, FlatStyle = FlatStyle.Flat, Cursor = Cursors.Hand };
            compactButton.FlatAppearance.BorderColor = Color.FromArgb(198, 213, 206);
            Action shrinkWindow = () =>
            {
                WindowState = FormWindowState.Normal;
                expandedSize = Size;
                timeOnly = true;
                face.TimeOnly = true;
                MinimumSize = new Size(80, 40);
                FormBorderStyle = FormBorderStyle.None;
                Size = new Size(80, 40);
                face.Invalidate();
            };
            compactButton.Click += (sender, args) => shrinkWindow();
            right.Controls.Add(compactButton);
            ToolTip windowTips = new ToolTip();
            windowTips.SetToolTip(compactButton, "缩小到 80×40");

            Button narrowCompactButton = new Button { Text = "缩小", Width = 70, Height = 28, Top = 32, BackColor = dark, ForeColor = Color.White, FlatStyle = FlatStyle.Flat, Cursor = Cursors.Hand };
            narrowCompactButton.FlatAppearance.BorderColor = Color.FromArgb(96, 120, 112);
            narrowCompactButton.Click += (sender, args) => shrinkWindow();
            left.Controls.Add(narrowCompactButton);
            windowTips.SetToolTip(narrowCompactButton, "缩小到 80×40");

            Action expandWindow = () =>
            {
                timeOnly = false;
                face.TimeOnly = false;
                FormBorderStyle = FormBorderStyle.Sizable;
                MinimumSize = new Size(200, 200);
                Size = expandedSize;
                CenterToScreen();
                face.Invalidate();
            };
            face.DoubleClick += (sender, args) => { if (timeOnly) expandWindow(); };
            face.MouseDown += (sender, args) => { if (timeOnly && args.Button == MouseButtons.Left) dragOrigin = args.Location; };
            face.MouseMove += (sender, args) =>
            {
                if (timeOnly && args.Button == MouseButtons.Left)
                    Location = new Point(Location.X + args.X - dragOrigin.X, Location.Y + args.Y - dragOrigin.Y);
            };
            ContextMenuStrip miniMenu = new ContextMenuStrip();
            miniMenu.Items.Add("展开", null, (sender, args) => expandWindow());
            miniMenu.Items.Add("退出", null, (sender, args) => Close());
            face.ContextMenuStrip = miniMenu;
            windowTips.SetToolTip(face, "双击展开；拖动可移动");

            Button expandButton = new Button { Text = "展开", Width = 36, Height = 23, BackColor = dark, ForeColor = Color.White, FlatStyle = FlatStyle.Flat, Cursor = Cursors.Hand };
            expandButton.FlatAppearance.BorderColor = Color.FromArgb(96, 120, 112);
            expandButton.Click += (sender, args) => expandWindow();
            left.Controls.Add(expandButton);
            windowTips.SetToolTip(expandButton, "恢复完整窗口");

            Panel modePanel = new Panel { Width = 346, Height = 43, BackColor = Color.FromArgb(43, 65, 59), Anchor = AnchorStyles.Top };
            left.Controls.Add(modePanel);
            string[] names = { "专注", "短休息", "长休息" };
            for (int i = 0; i < 3; i++)
            {
                int selected = i;
                Button button = new Button { Text = names[i], FlatStyle = FlatStyle.Flat, Width = 110, Height = 33, Left = 4 + i * 114, Top = 5, Cursor = Cursors.Hand };
                button.FlatAppearance.BorderSize = 0;
                button.Click += (sender, args) => SwitchPhase((Phase)selected);
                modeButtons[i] = button;
                modePanel.Controls.Add(button);
            }

            face.SetBounds(0, 0, 360, 360);
            left.Controls.Add(face);
            startButton.Text = "开始专注";
            startButton.BackColor = coral;
            startButton.ForeColor = dark;
            startButton.FlatStyle = FlatStyle.Flat;
            startButton.FlatAppearance.BorderSize = 0;
            startButton.Font = new Font("Microsoft YaHei", 12, FontStyle.Bold);
            startButton.Cursor = Cursors.Hand;
            startButton.SetBounds(0, 0, 150, 48);
            startButton.Click += (sender, args) => ToggleClock();
            left.Controls.Add(startButton);
            Button reset = new Button { Text = "重置", BackColor = dark, ForeColor = Color.White, FlatStyle = FlatStyle.Flat, Cursor = Cursors.Hand };
            reset.FlatAppearance.BorderColor = Color.FromArgb(96, 120, 112);
            reset.SetBounds(0, 0, 90, 48);
            reset.Click += (sender, args) => ResetClock();
            left.Controls.Add(reset);
            Label foot = TextLabel("每完成 4 次专注，安排一次长休息", 9, Color.FromArgb(164, 187, 178));
            foot.SetBounds(34, 0, 380, 24);
            left.Controls.Add(foot);
            Font compactFont = new Font("Microsoft YaHei", 8);
            Font compactBoldFont = new Font("Microsoft YaHei", 8, FontStyle.Bold);
            Font normalModeFont = new Font("Microsoft YaHei", 10);
            Font normalStartFont = new Font("Microsoft YaHei", 12, FontStyle.Bold);
            Action layoutLeft = () =>
            {
                if (timeOnly)
                {
                    foreach (Control control in left.Controls) control.Visible = control == face;
                    face.SetBounds(0, 0, left.ClientSize.Width, left.ClientSize.Height);
                    return;
                }
                modePanel.Visible = startButton.Visible = reset.Visible = true;
                int center = left.ClientSize.Width / 2;
                bool compact = left.ClientSize.Width < 600 || left.ClientSize.Height < 550;
                brand.Visible = soundBox.Visible = foot.Visible = !compact;
                narrowCompactButton.Visible = !compact && !right.Visible;
                narrowCompactButton.Left = left.ClientSize.Width - 86;
                soundBox.Left = left.ClientSize.Width - (narrowCompactButton.Visible ? 240 : 145);
                expandButton.Visible = compact;
                if (compact)
                {
                    int width = left.ClientSize.Width;
                    int height = left.ClientSize.Height;
                    expandButton.SetBounds(width - 40, 32, 36, 23);
                    expandButton.Font = compactFont;
                    modePanel.SetBounds(center - Math.Min(300, width - 8) / 2, 2, Math.Min(300, width - 8), 24);
                    int buttonWidth = (modePanel.Width - 8) / 3;
                    for (int i = 0; i < 3; i++)
                    {
                        modeButtons[i].SetBounds(4 + i * buttonWidth, 2, buttonWidth, 20);
                        modeButtons[i].Font = compactFont;
                    }
                    int faceSize = Math.Max(1, Math.Min(340, Math.Min(width - 8, height - 58)));
                    face.SetBounds(center - faceSize / 2, modePanel.Bottom + 1, faceSize, faceSize);
                    int actionsTop = height - 29;
                    int startWidth = Math.Min(100, Math.Max(72, (width - 20) * 3 / 5));
                    int resetWidth = Math.Min(65, Math.Max(48, width - startWidth - 20));
                    int actionsLeft = center - (startWidth + resetWidth + 6) / 2;
                    startButton.SetBounds(actionsLeft, actionsTop, startWidth, 25);
                    startButton.Font = compactBoldFont;
                    reset.SetBounds(actionsLeft + startWidth + 6, actionsTop, resetWidth, 25);
                    reset.Font = compactFont;
                }
                else
                {
                    modePanel.SetBounds(center - 173, Math.Max(84, left.ClientSize.Height / 2 - 255), 346, 43);
                    for (int i = 0; i < 3; i++)
                    {
                        modeButtons[i].SetBounds(4 + i * 114, 5, 110, 33);
                        modeButtons[i].Font = normalModeFont;
                    }
                    face.SetBounds(center - 180, modePanel.Bottom + 10, 360, 360);
                    startButton.SetBounds(center - 127, face.Bottom + 4, 150, 48);
                    startButton.Font = normalStartFont;
                    reset.SetBounds(center + 37, startButton.Top, 90, 48);
                    reset.Font = normalModeFont;
                    foot.Top = left.ClientSize.Height - 37;
                }
            };
            left.Resize += (sender, args) => layoutLeft();
            ClientSizeChanged += (sender, args) =>
            {
                right.Visible = !timeOnly && ClientSize.Width >= 760 && ClientSize.Height >= 600;
                layoutLeft();
            };
            right.Visible = ClientSize.Width >= 760 && ClientSize.Height >= 600;
            layoutLeft();

            Label todayTitle = TextLabel("今日进度", 10, Color.FromArgb(102, 124, 116), true);
            todayTitle.SetBounds(32, 45, 130, 28);
            right.Controls.Add(todayTitle);
            countLabel.Font = new Font("Segoe UI", 38, FontStyle.Bold);
            countLabel.ForeColor = dark;
            countLabel.SetBounds(32, 80, 110, 70);
            right.Controls.Add(countLabel);
            Label countUnit = TextLabel("次专注完成", 10, Color.FromArgb(89, 110, 101));
            countUnit.SetBounds(142, 115, 130, 28);
            right.Controls.Add(countUnit);
            AddRule(right, 165);
            Label untilTitle = TextLabel("距长休息", 10, Color.FromArgb(102, 124, 116));
            untilTitle.SetBounds(32, 185, 110, 28);
            right.Controls.Add(untilTitle);
            ConfigureValueLabel(untilLabel, 160, 185, 120, right);
            AddRule(right, 242);
            Label settingsTitle = TextLabel("计时设置 · 分钟", 10, Color.FromArgb(102, 124, 116), true);
            settingsTitle.SetBounds(32, 267, 230, 26);
            right.Controls.Add(settingsTitle);
            for (int i = 0; i < 3; i++)
            {
                int selected = i;
                Label label = TextLabel(names[i], 10, dark);
                label.SetBounds(32, 311 + i * 53, 115, 30);
                right.Controls.Add(label);
                NumericUpDown input = new NumericUpDown { Minimum = 1, Maximum = i == 0 ? 180 : 60, Value = minutes[i], Width = 78, Height = 30, Left = 194, Top = 308 + i * 53, TextAlign = HorizontalAlignment.Center, BackColor = Color.White };
                input.ValueChanged += (sender, args) =>
                {
                    minutes[selected] = (int)input.Value;
                    if ((int)phase == selected) ResetClock();
                    else { SaveState(); RefreshUi(); }
                };
                durationInputs[i] = input;
                right.Controls.Add(input);
            }
            Label hint = TextLabel("修改当前模式的时长后，计时器会重新开始。", 8, Color.FromArgb(108, 128, 118));
            hint.SetBounds(32, 472, 260, 35);
            right.Controls.Add(hint);
            AddRule(right, 520);
            Label nextTitle = TextLabel("下一阶段", 9, Color.FromArgb(102, 124, 116));
            nextTitle.SetBounds(32, 535, 100, 22);
            right.Controls.Add(nextTitle);
            ConfigureValueLabel(nextLabel, 150, 532, 122, right);
            right.Resize += (sender, args) =>
            {
                nextTitle.Top = right.ClientSize.Height - 68;
                nextLabel.Top = right.ClientSize.Height - 71;
            };
        }

        private Label ConfigureValueLabel(Label label, int x, int y, int width, Control parent)
        {
            label.Font = new Font("Microsoft YaHei", 11, FontStyle.Bold);
            label.ForeColor = dark;
            label.TextAlign = ContentAlignment.MiddleRight;
            label.SetBounds(x, y, width, 30);
            parent.Controls.Add(label);
            return label;
        }

        private static Label TextLabel(string text, float size, Color color, bool bold = false)
        {
            return new Label { Text = text, AutoSize = false, Font = new Font("Microsoft YaHei", size, bold ? FontStyle.Bold : FontStyle.Regular), ForeColor = color, BackColor = Color.Transparent };
        }

        private static void AddRule(Control parent, int y)
        {
            parent.Controls.Add(new Panel { Left = 32, Top = y, Width = 240, Height = 1, BackColor = Color.FromArgb(217, 227, 222) });
        }

        private int CurrentSeconds()
        {
            return deadline.HasValue ? Math.Max(0, (int)Math.Ceiling((deadline.Value - DateTime.UtcNow).TotalSeconds)) : remaining;
        }

        private Phase NextPhase()
        {
            return phase == Phase.Focus ? (completed > 0 && completed % 4 == 0 ? Phase.LongBreak : Phase.ShortBreak) : Phase.Focus;
        }

        private void RefreshUi()
        {
            int seconds = CurrentSeconds();
            face.TimeText = string.Format("{0:00}:{1:00}", seconds / 60, seconds % 60);
            face.PhaseText = phase == Phase.Focus ? "专注时间" : phase == Phase.ShortBreak ? "短休息时间" : "长休息时间";
            face.StatusText = notice ?? (deadline.HasValue ? "进行中" : seconds == minutes[(int)phase] * 60 ? "准备开始" : "已暂停");
            face.Progress = 1 - (double)seconds / (minutes[(int)phase] * 60);
            face.Invalidate();
            startButton.Text = deadline.HasValue ? "暂停" : phase == Phase.Focus ? "开始专注" : "开始休息";
            countLabel.Text = completed.ToString();
            untilLabel.Text = (4 - completed % 4) + " 次专注";
            nextLabel.Text = NextPhase() == Phase.Focus ? "专注" : NextPhase() == Phase.ShortBreak ? "短休息" : "长休息";
            for (int i = 0; i < 3; i++)
            {
                bool selected = i == (int)phase;
                modeButtons[i].BackColor = selected ? paper : Color.FromArgb(43, 65, 59);
                modeButtons[i].ForeColor = selected ? dark : Color.FromArgb(188, 206, 198);
            }
            Text = face.TimeText + " · " + face.PhaseText + " | 番茄时钟";
        }

        private void SwitchPhase(Phase selected)
        {
            phase = selected;
            deadline = null;
            remaining = minutes[(int)phase] * 60;
            notice = null;
            SaveState();
            RefreshUi();
        }

        private void ToggleClock()
        {
            notice = null;
            if (deadline.HasValue) { remaining = CurrentSeconds(); deadline = null; }
            else deadline = DateTime.UtcNow.AddSeconds(remaining);
            SaveState();
            RefreshUi();
        }

        private void ResetClock()
        {
            deadline = null;
            remaining = minutes[(int)phase] * 60;
            notice = null;
            SaveState();
            RefreshUi();
        }

        private void TickClock()
        {
            if (DateTime.Today != statisticsDay)
            {
                statisticsDay = DateTime.Today;
                completed = 0;
                SaveState();
                RefreshUi();
            }
            if (!deadline.HasValue) return;
            if (DateTime.UtcNow >= deadline.Value)
            {
                Phase finished = phase;
                if (phase == Phase.Focus) completed++;
                phase = NextPhase();
                remaining = minutes[(int)phase] * 60;
                deadline = null;
                notice = finished == Phase.Focus ? "专注完成" : "休息完成";
                if (soundBox.Checked) SystemSounds.Asterisk.Play();
                SaveState();
            }
            RefreshUi();
        }

        private void LoadState()
        {
            remaining = minutes[0] * 60;
            try
            {
                if (!File.Exists(statePath)) return;
                XElement root = XElement.Load(statePath);
                for (int i = 0; i < 3; i++)
                {
                    int value;
                    if (int.TryParse((string)root.Attribute("minutes" + i), out value) && value >= 1 && value <= (i == 0 ? 180 : 60)) minutes[i] = value;
                }
                int phaseValue;
                if (int.TryParse((string)root.Attribute("phase"), out phaseValue) && phaseValue >= 0 && phaseValue <= 2) phase = (Phase)phaseValue;
                int storedRemaining;
                if (int.TryParse((string)root.Attribute("remaining"), out storedRemaining)) remaining = Math.Max(0, Math.Min(storedRemaining, minutes[(int)phase] * 60));
                else remaining = minutes[(int)phase] * 60;
                DateTime storedDay;
                if (DateTime.TryParse((string)root.Attribute("day"), out storedDay) && storedDay.Date == DateTime.Today)
                {
                    int storedCount;
                    if (int.TryParse((string)root.Attribute("completed"), out storedCount)) completed = Math.Max(0, storedCount);
                }
                long ticks;
                if (long.TryParse((string)root.Attribute("deadline"), out ticks) && ticks > 0) deadline = new DateTime(ticks, DateTimeKind.Utc);
                soundEnabled = (string)root.Attribute("sound") != "0";
            }
            catch { remaining = minutes[(int)phase] * 60; deadline = null; }
        }

        private void SaveState()
        {
            try
            {
                Directory.CreateDirectory(Path.GetDirectoryName(statePath));
                new XElement("pomodoro",
                    new XAttribute("day", statisticsDay.ToString("yyyy-MM-dd")),
                    new XAttribute("completed", completed),
                    new XAttribute("phase", (int)phase),
                    new XAttribute("remaining", CurrentSeconds()),
                    new XAttribute("deadline", deadline.HasValue ? deadline.Value.Ticks : 0),
                    new XAttribute("minutes0", minutes[0]),
                    new XAttribute("minutes1", minutes[1]),
                    new XAttribute("minutes2", minutes[2]),
                    new XAttribute("sound", soundBox.Checked ? 1 : 0)).Save(statePath);
            }
            catch { }
        }

        [STAThread]
        private static void Main()
        {
            Application.EnableVisualStyles();
            Application.SetCompatibleTextRenderingDefault(false);
            Application.Run(new MainForm());
        }
    }
}
