<template>
  <div id="app">
    <header class="site-header">
      <div class="header-inner">
        <span class="logo">Portfolio</span>
        <nav>
          <a v-for="item in navItems" :key="item.id" :href="item.href">{{ item.label }}</a>
        </nav>
      </div>
    </header>
    <main>
      <router-view />
    </main>
    <footer class="site-footer">
      <p>&copy; 2025 冯家宝. All Rights Reserved.</p>
    </footer>
  </div>
</template>

<script>
export default {
  name: 'App',
  data() {
    return {
      navItems: [
        { id: 1, label: '首页', href: '#' },
        { id: 2, label: '关于', href: '#about' },
        { id: 3, label: '技能', href: '#skills' },
        { id: 4, label: '项目', href: '#projects' },
        { id: 5, label: '联系', href: '#contact' }
      ]
    }
  }
}
</script>

<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif; color: #333; background: #f8fafc; }
.site-header { position: fixed; top: 0; left: 0; right: 0; z-index: 100; background: rgba(255,255,255,0.95); backdrop-filter: blur(10px); box-shadow: 0 1px 10px rgba(0,0,0,0.06); }
.header-inner { max-width: 1200px; margin: 0 auto; padding: 0 24px; height: 64px; display: flex; align-items: center; justify-content: space-between; }
.logo { font-size: 22px; font-weight: 700; color: #409eff; }
nav { display: flex; gap: 32px; }
nav a { text-decoration: none; color: #555; font-size: 15px; transition: color 0.2s; cursor: pointer; }
nav a:hover { color: #409eff; }
main { min-height: calc(100vh - 120px); }
.site-footer { height: 60px; display: flex; align-items: center; justify-content: center; color: #999; font-size: 14px; border-top: 1px solid #eee; }
</style>