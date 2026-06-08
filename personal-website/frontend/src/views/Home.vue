<template>
  <div class="home">
    <!-- Hero -->
    <section class="hero" id="home">
      <div class="container">
        <div class="hero-avatar">{{ initials }}</div>
        <h1 class="hero-name">{{ user.name }}</h1>
        <p class="hero-title">{{ user.title }}</p>
        <p class="hero-bio">{{ user.bio }}</p>
        <div class="hero-links">
          <a v-if="user.github" :href="user.github" target="_blank">
            <el-button type="default" round>GitHub</el-button>
          </a>
          <a v-if="user.email" :href="'mailto:' + user.email">
            <el-button type="primary" round>联系我</el-button>
          </a>
        </div>
      </div>
    </section>

    <!-- About -->
    <section class="about" id="about">
      <div class="container">
        <h2 class="section-title">关于我</h2>
        <div class="about-grid">
          <div class="about-card" v-for="item in aboutItems" :key="item.label">
            <div class="about-icon">{{ item.icon }}</div>
            <div class="about-label">{{ item.label }}</div>
            <div class="about-value">{{ item.value }}</div>
          </div>
        </div>
        <!-- Additional personal info -->
        <div class="person-detail" style="max-width:900px;margin:40px auto 0;padding:32px;background:#fff;border-radius:12px;box-shadow:0 2px 12px rgba(0,0,0,0.06);">
          <h3 style="margin-bottom:20px;color:#1a1a2e;font-size:20px;">求职意向</h3>
          <div class="job-grid" style="display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-bottom:28px;">
            <div><span style="color:#999;font-size:13px;">意向岗位</span><p style="font-weight:600;">智能体应用开发</p></div>
            <div><span style="color:#999;font-size:13px;">意向城市</span><p style="font-weight:600;">上海</p></div>
            <div><span style="color:#999;font-size:13px;">期望薪资</span><p style="font-weight:600;">7k-9k</p></div>
            <div><span style="color:#999;font-size:13px;">当前状态</span><p style="font-weight:600;color:#67c23a;">随时到岗</p></div>
          </div>

          <h3 style="margin-bottom:16px;color:#1a1a2e;font-size:20px;">个人优势</h3>
          <div style="display:grid;grid-template-columns:repeat(2,1fr);gap:12px;">
            <div class="advantage-item" v-for="adv in advantages" :key="adv.title" style="background:#f8fafc;padding:16px;border-radius:8px;border-left:3px solid #409eff;">
              <strong style="display:block;margin-bottom:6px;">{{ adv.title }}</strong>
              <span style="font-size:14px;color:#666;line-height:1.6;">{{ adv.desc }}</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Skills -->
    <section class="skills" id="skills">
      <div class="container">
        <h2 class="section-title">专业技能</h2>
        <div class="skills-grid">
          <div class="skill-card" v-for="skill in skills" :key="skill.id">
            <div class="skill-name">{{ skill.name }}</div>
            <div class="skill-bar">
              <div class="skill-fill" :style="{ width: skill.level + '%' }"></div>
            </div>
            <div class="skill-level">{{ skill.level }}%</div>
          </div>
        </div>
      </div>
    </section>

    <!-- Projects -->
    <section class="projects" id="projects">
      <div class="container">
        <h2 class="section-title">项目经历</h2>
        <div class="projects-grid">
          <div class="project-card" v-for="project in projects" :key="project.id">
            <div class="project-header">
              <h3>{{ project.name }}</h3>
            </div>
            <p class="project-desc">{{ project.description }}</p>
            <div class="project-tags">
              <el-tag v-for="(tag, idx) in parseJson(project.tech_stack)" :key="idx" size="small" type="info">{{ tag }}</el-tag>
            </div>
            <div class="project-highlights" v-if="project.highlights">
              <ul>
                <li v-for="(h, idx) in parseJson(project.highlights)" :key="idx">{{ h }}</li>
              </ul>
            </div>
            <div class="project-links">
              <a v-if="project.github_url" :href="project.github_url" target="_blank">
                <el-button size="small" type="default">源码</el-button>
              </a>
              <a v-if="project.demo_url" :href="project.demo_url" target="_blank">
                <el-button size="small" type="primary">演示</el-button>
              </a>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Contact -->
    <section class="contact" id="contact">
      <div class="container">
        <h2 class="section-title">联系我</h2>
        <div class="contact-wrapper">
          <div class="contact-info">
            <div class="info-item" v-if="user.email">
              <span class="info-label">邮箱</span>
              <span class="info-value">{{ user.email }}</span>
            </div>
            <div class="info-item" v-if="user.phone">
              <span class="info-label">电话</span>
              <span class="info-value">{{ user.phone }}</span>
            </div>
            <div class="info-item" v-if="user.location">
              <span class="info-label">城市</span>
              <span class="info-value">{{ user.location }}</span>
            </div>
          </div>
          <div class="contact-form-box">
            <el-form :model="form" label-position="top">
              <el-form-item label="姓名">
                <el-input v-model="form.name" placeholder="请输入您的姓名" />
              </el-form-item>
              <el-form-item label="邮箱">
                <el-input v-model="form.email" placeholder="请输入您的邮箱" />
              </el-form-item>
              <el-form-item label="主题">
                <el-input v-model="form.subject" placeholder="请输入主题" />
              </el-form-item>
              <el-form-item label="留言">
                <el-input v-model="form.content" type="textarea" :rows="4" placeholder="请输入留言内容" />
              </el-form-item>
              <el-button type="primary" @click="handleSubmit" :loading="submitting" round>
                {{ submitting ? '发送中...' : '发送留言' }}
              </el-button>
            </el-form>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script>
import { getHomeData, submitContact } from '../api'

export default {
  name: 'Home',
  data() {
    return {
      user: { name: '冯家宝', title: '', bio: '', github: '', email: '', phone: '', location: '' },
      skills: [],
      projects: [],
      form: { name: '', email: '', subject: '', content: '' },
      submitting: false,
      advantages: [
        { title: 'Python开发能力', desc: '熟练掌握Python语言，能够运用其进行高效的程序开发，支持业务功能的快速实现与迭代。' },
        { title: '数据库操作能力', desc: '精通MySQL数据库，熟练编写SQL语句完成各种操作，保障数据处理的准确性与效率。' },
        { title: 'Web框架应用能力', desc: '熟练运用Django框架进行Web应用开发，熟悉MVT架构模式，可快速搭建稳定、高效的Web项目。' },
        { title: '大模型工具链掌握', desc: '熟练运用LangChain核心组件，具备Agent设计与开发能力，熟练掌握AVG框架，支持构建基于大模型的应用系统。' },
        { title: '开源大模型部署', desc: '熟练部署本地OpenClaw智能体，掌握Coze工作流、插件调用与智能体配置，可快速落地AI应用。' },
        { title: '全栈开发能力', desc: '熟练掌握Django后端框架和Vue前端技术栈，能够独立完成从需求分析到产品落地的全流程开发。' }
      ]
    }
  },
  computed: {
    initials() {
      return this.user.name ? this.user.name.charAt(0) : '?'
    },
    aboutItems() {
      return [
        { icon: '\ud83d\udc64', label: '姓名', value: this.user.name || '-' },
        { icon: '\ud83d\udc68\u200d\ud83d\udcbb', label: '职位', value: this.user.title || '-' },
        { icon: '\ud83d\udce7', label: '邮箱', value: this.user.email || '-' },
        { icon: '\ud83d\udcf1', label: '电话', value: this.user.phone || '-' }
      ]
    }
  },
  methods: {
    parseJson(str) {
      if (!str) return []
      try {
        return JSON.parse(str)
      } catch {
        return str.replace(/[\[\]"]/g, '').split(',').map(s => s.trim())
      }
    },
    async fetchData() {
      try {
        const res = await getHomeData()
        if (res.data.user) this.user = res.data.user
        this.skills = res.data.skills || []
        this.projects = res.data.projects || []
      } catch (e) {
        console.error('Failed to fetch data:', e)
      }
    },
    async handleSubmit() {
      if (!this.form.name || !this.form.email || !this.form.content) {
        this.$message.warning('请填写必填项（姓名、邮箱、留言内容）')
        return
      }
      this.submitting = true
      try {
        await submitContact(this.form)
        this.$message.success('留言已发送，感谢您的联系！')
        this.form = { name: '', email: '', subject: '', content: '' }
      } catch (e) {
        this.$message.error('发送失败，请稍后重试')
      } finally {
        this.submitting = false
      }
    }
  },
  mounted() {
    this.fetchData()
  }
}
</script>

<style scoped>
.container { max-width: 1200px; margin: 0 auto; padding: 0 24px; }
.section-title { text-align: center; font-size: 32px; font-weight: 700; margin-bottom: 48px; color: #1a1a2e; position: relative; }
.section-title::after { content: ''; display: block; width: 60px; height: 4px; background: #409eff; margin: 12px auto 0; border-radius: 2px; }

/* Hero */
.hero { padding: 140px 0 80px; text-align: center; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: #fff; }
.hero-avatar { width: 100px; height: 100px; border-radius: 50%; background: rgba(255,255,255,0.2); margin: 0 auto 24px; display: flex; align-items: center; justify-content: center; font-size: 40px; font-weight: 700; border: 3px solid rgba(255,255,255,0.4); }
.hero-name { font-size: 42px; font-weight: 700; margin-bottom: 8px; }
.hero-title { font-size: 20px; opacity: 0.9; margin-bottom: 16px; }
.hero-bio { font-size: 16px; opacity: 0.8; max-width: 600px; margin: 0 auto 32px; line-height: 1.7; }
.hero-links { display: flex; gap: 16px; justify-content: center; }

/* About */
.about { padding: 80px 0; }
.about-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 24px; }
.about-card { background: #fff; border-radius: 12px; padding: 32px 20px; text-align: center; box-shadow: 0 2px 12px rgba(0,0,0,0.06); transition: transform 0.2s; }
.about-card:hover { transform: translateY(-4px); }
.about-icon { font-size: 32px; margin-bottom: 12px; }
.about-label { font-size: 13px; color: #999; margin-bottom: 6px; }
.about-value { font-size: 16px; color: #333; font-weight: 500; }
.advantage-item { transition: all 0.2s; }
.advantage-item:hover { transform: translateY(-2px); box-shadow: 0 2px 8px rgba(0,0,0,0.08); }

/* Skills */
.skills { padding: 80px 0; background: #fff; }
.skills-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; }
.skill-card { background: #f8fafc; border-radius: 10px; padding: 20px 24px; display: flex; align-items: center; gap: 16px; }
.skill-name { width: 120px; font-weight: 600; font-size: 15px; }
.skill-bar { flex: 1; height: 10px; background: #e4e7ed; border-radius: 5px; overflow: hidden; }
.skill-fill { height: 100%; background: linear-gradient(90deg, #409eff, #67c23a); border-radius: 5px; transition: width 1s ease; }
.skill-level { width: 44px; text-align: right; font-size: 14px; color: #666; }

/* Projects */
.projects { padding: 80px 0; }
.projects-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 24px; }
.project-card { background: #fff; border-radius: 12px; padding: 28px; box-shadow: 0 2px 12px rgba(0,0,0,0.06); transition: transform 0.2s, box-shadow 0.2s; }
.project-card:hover { transform: translateY(-4px); box-shadow: 0 6px 20px rgba(0,0,0,0.1); }
.project-header h3 { font-size: 18px; margin-bottom: 12px; color: #1a1a2e; }
.project-desc { font-size: 14px; color: #666; line-height: 1.6; margin-bottom: 16px; }
.project-tags { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 16px; }
.project-highlights ul { padding-left: 18px; margin-bottom: 16px; }
.project-highlights li { font-size: 13px; color: #888; line-height: 1.8; }
.project-links { display: flex; gap: 10px; }

/* Contact */
.contact { padding: 80px 0; background: #fff; }
.contact-wrapper { display: grid; grid-template-columns: 1fr 2fr; gap: 48px; max-width: 900px; margin: 0 auto; }
.contact-info { display: flex; flex-direction: column; gap: 24px; }
.info-item { display: flex; flex-direction: column; gap: 4px; }
.info-label { font-size: 13px; color: #999; }
.info-value { font-size: 16px; color: #333; }
.contact-form-box { background: #f8fafc; padding: 32px; border-radius: 12px; }

@media (max-width: 900px) {
  .about-grid { grid-template-columns: repeat(2, 1fr); }
  .skills-grid { grid-template-columns: 1fr; }
  .projects-grid { grid-template-columns: 1fr; }
  .contact-wrapper { grid-template-columns: 1fr; }
}
</style>